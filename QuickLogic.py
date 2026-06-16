import argparse
import zipfile
import sys
import os
import io
from sigrok.sigrok import Sigrok, ConfigKey
from colorama import Fore, Style, init

print(r"""
   ____       _      _      __             _      
  /___ \_   _(_) ___| | __ / /  ___   __ _(_) ___ 
 //  / / | | | |/ __| |/ // /  / _ \ / _` | |/ __|
/ \_/ /| |_| | | (__|   </ /__| (_) | (_| | | (__ 
\___,_\ \__,_|_|\___|_|\_\____/\___/ \__, |_|\___|
                                     |___/        
The automated logic capture tool for hardware enumeration
""")

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, metavar="IoT_Capture", help="Name of the saved capture file")
parser.add_argument("--ch", metavar="0,4,7", help="This is to specify the channels to listen on the logic analyzer (comma separated)")
parser.add_argument("-cs", "--speed", type=int, metavar="4000000", help="This is to set the capture speed to something other than default (4000000)")
parser.add_argument("-s", "--size", type=int, metavar="10000000", help="This is to set the capture size to something other than default (10000000)")
parser.add_argument("--timeout", type=int, metavar="30", help="This will set a timeout value other than the default 15 seconds")
parser.add_argument("--analyze", action='store_true', help="This is for skipping the capture portion and just analyzing a saved capture")
arguments = parser.parse_args()

init(autoreset=True)

## Constants section
channel_data = {}
active_CHANNELS = []
DRIVER_NAME = 'fx2lafw' ## In future versions this will be fixed to work with other types of LA's
chunk_size = 4194304
Findings = {}

### This will be for grabbing the user defined capture speed or using the default
if arguments.speed:
    SAMPLE_RATE = arguments.speed
else:
    SAMPLE_RATE = 4000000

### This will be for grabbing the user defined capture size or using the default
if arguments.size:
    ReadSize = arguments.size
else:
    ReadSize = 100000000

### This is to set the timeout from user input
if arguments.timeout:
    ReadTimeout = arguments.timeout
else:
    ReadTimeout = 15

## Checks for and appends the filename with the .sr file extension if needed
if not arguments.file.endswith(".sr"):
    CaptureFile = arguments.file + ".sr"
else:
    CaptureFile = arguments.file

### This takes the input for ch and splits them at the comma and ensures they all fit between 0-7. If not it throws an error
if arguments.ch:
    channels = [int(ch.strip()) for ch in arguments.ch.split(",")]
    if not all(0 <= ch <= 7 for ch in channels):
        parser.error(Fore.RED + "Channels must be between 0 and 7")
    else:
        CHANNELS = channels
else:
    CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7]


## Function to use the logic device selected and proceed to run a capture
def run_capture(SAMPLE_RATE, ReadSize, CHANNELS, CaptureFile):
	sr = Sigrok()
	sr.init()
	driver = sr.get_driver(DRIVER_NAME)
	driver.init()
	devices = driver.scan()
	if not devices:
		print(f"{Fore.RED}No devices were detected")
		sys.exit()

	print(f"{Fore.CYAN}Which device should we use?")
	for index, device in enumerate(devices, start=1):
		print(f"{index}: {device.vendor} {device.model}")

	device_selection = int(input("\nSelect the device: "))
	if 1 <= device_selection <= len(devices):
		device = devices[device_selection - 1]
		print(f"{Fore.GREEN}\nUsing: {device.vendor} {device.model}")
	else:
		print(f"{Fore.RED}Invalid selection")
		sys.exit()

	device.open()
	device.set_config_uint64(ConfigKey.SR_CONF_SAMPLERATE, SAMPLE_RATE)
	device.set_config_uint64(ConfigKey.SR_CONF_LIMIT_SAMPLES, ReadSize)
	channel_strings = [f"D{ch}" for ch in CHANNELS]
	device.enable_channels(*channel_strings)
	session = sr.session(devices=device)
	session.start()
	print(f"{Fore.CYAN}Capturing...")

	## Begin Capture
	raw_data = bytearray()
	packet_count = 0

	while True:
		packet = session.next_packet(timeout=ReadTimeout)

		if packet is None:
			print(f"{Fore.YELLOW}Timeout - no data received")
			break

		if type(packet).__name__ == "EndPacket":
			break

		if type(packet).__name__ == "LogicPacket":
			raw_data.extend(packet.data)
			packet_count += 1

	session.stop()
	device.close()
	print(f"{Fore.CYAN}Done capturing")

	### Build the .sr file
	samplerate_mhz = SAMPLE_RATE / 1_000_000
	probe_lines = "\n".join([f"probe{i+1}=D{ch}" for i, ch in enumerate(CHANNELS)])
	metadata = f"""[global]
sigrok version=0.6.0-git-883c2ac

[device 1]
capturefile=logic-1
total probes={len(CHANNELS)}
samplerate={samplerate_mhz} MHz
total analog=0
{probe_lines}
unitsize=1
"""
	### Split raw data into 4MB chunks
	chunks = [raw_data[i:i+chunk_size] for i in range(0, len(raw_data), chunk_size)]

	### Write the .sr zip file
	with zipfile.ZipFile(CaptureFile, 'w', zipfile.ZIP_DEFLATED) as zf:
		zf.writestr("version", "2")
		zf.writestr("metadata", metadata)
		for i, chunk in enumerate(chunks, start=1):
			zf.writestr(f"logic-1-{i}", bytes(chunk))

	print(f"{Fore.GREEN}Capture saved to {CaptureFile} with {len(chunks)} chunks")


## This is the list of analyze functions
## Check for UART function
def UART_Check(bits, SAMPLE_RATE, CaptureFile, pin):
	## This gets a sample to test for ascii percentage before fully committing the entire capture to decode
	print(f"{Fore.CYAN}Analyzing for UART...")
	signal_start = bits.index(0)
	actual_spb = 0
	while bits[signal_start + actual_spb] == 0:
		actual_spb += 1
	samples_per_bit = actual_spb
	signal_stagger = round(samples_per_bit / 2)
	decoded_data = ""
	binary_data = []
	bytes_collected = 0

	while bytes_collected < 100:
		data_start = signal_start + samples_per_bit + signal_stagger
		try:
			for b in range(8):
				position = data_start + (b * samples_per_bit)
				binary_data.append(bits[position])
		except Exception:
			print(f"{Fore.RED}An error occurred reading the capture")
		create_byte = ''.join(map(str, binary_data))
		decoded_data += chr(int(create_byte[::-1], 2))
		binary_data = []
		try:
			search_from = position + samples_per_bit
			signal_start = search_from + bits[search_from:].index(0)
		except ValueError:
			break
		bytes_collected += 1

	printable_characters = 0
	for char in decoded_data:
		if char.isprintable():
			printable_characters += 1

	print_percent = printable_characters / len(decoded_data)

	if print_percent * 100 >= 90:
		sr = "samplerate"
		with zipfile.ZipFile(CaptureFile, "r", zipfile.ZIP_DEFLATED) as zf:
			with zf.open("metadata", "r") as f:
					with io.TextIOWrapper(f, encoding='utf-8') as data:
						for line_num, line in enumerate(data, 1):
							if sr in line:
								raw_data = line.strip()
								main = raw_data.split("=", 1)[1]
								number = main.split(" ", 1)[0]
								unit = main.split(" ", 1)[1]
								if unit == "MHz":
									SampleRate = int(float(number) * 1000000)
								elif unit == "kHz":
									SampleRate = int(float(number) * 1000)
								else:
									SampleRate = int(number)
		baud = int(SampleRate / samples_per_bit)
		print(f"{Fore.GREEN}We got a match of {print_percent:.0%} for UART TX using {baud} baud rate on channel: {pin}")
		Findings[pin] = f"Most likely UART Tx @ {baud} baud rate"
		while True:
			print(f"{Style.BRIGHT}{Fore.CYAN}========= Decoded Sample =========\n{decoded_data}")
			response = input(f"{Fore.GREEN}A positive match was found! Would you like to print the decoded version to a file? (y/n): ").lower().strip()
			if response in ['y', 'yes']:
				root, ext = os.path.splitext(CaptureFile)
				Full_Decode_File = root + "_UART_Decode.txt"
				signal_start = bits.index(0)
				binary_data = []
				bytes_written = 0
				with open(Full_Decode_File, 'w') as d:
					d.write(f"Channel: {pin}\nBaudrate: {baud}\nBegin Decoded Capture\n=========================================\n")
					while True:
						data_start = signal_start + samples_per_bit + signal_stagger
						for b in range(8):
							position = data_start + (b * samples_per_bit)
							binary_data.append(bits[position])

						create_byte = ''.join(map(str, binary_data))
						d.write(chr(int(create_byte[::-1], 2)))
						d.flush()
						binary_data = []
						bytes_written += 1
						if bytes_written % 100 == 0:
							print(f"{Fore.CYAN}[*] Decoding... {bytes_written} bytes decoded", end='\r')
						try:
							search_from = position + samples_per_bit
							signal_start = search_from + bits[search_from:].index(0)
						except ValueError:
							break
				print(f"\n{Fore.GREEN}The Decoded capture is saved at {Full_Decode_File}")
				break
			elif response in ['n', 'no']:
				print(f"{Fore.YELLOW}Exiting...")
				break
			else:
				print(f"{Fore.RED}Invalid response please enter 'y' or 'n'.")
			break

	return decoded_data


if not arguments.analyze:
	run_capture(SAMPLE_RATE, ReadSize, CHANNELS, CaptureFile)

## Grabs .sr file and checks magic bytes to see if it is a correct zip
if zipfile.is_zipfile(CaptureFile):
	print(f"{Fore.GREEN}Capture file validated successfully")
else:
	print(f"{Fore.RED}Issues reading capture file please check!")
	sys.exit()

## reads .sr file and grabs the logic files that will be analyzed
raw_data = bytearray()

with zipfile.ZipFile(CaptureFile, 'r') as capture:
	files = capture.namelist()
	df = [f for f in files if f.startswith("logic-1")]

	## breaks down the logic files into one byte array
	print(f"{Fore.GREEN}Reading data in file...")
	for data_files in df:
		full_bytes = capture.read(data_files)
		raw_data.extend(full_bytes)

## This section performs a check for each channel to see if the channel idles high or low indicating no traffic and adds the active channels to an array
for channel in CHANNELS:
	bits = []
	for byte in raw_data:
		bit = (byte >> channel) & 1
		bits.append(bit)
	channel_data[channel] = bits
\
for channel, bits in channel_data.items():
	if len(set(bits)) != 1:
		active_CHANNELS.append(channel)
		print(f"{Fore.GREEN}Active channel on channel {channel}")
		Findings[channel] = "Unclassified"
	else:
		Findings[channel] = "No Traffic"


for channel in active_CHANNELS:
	UART_Check(channel_data[channel], SAMPLE_RATE, CaptureFile, channel)

print(f"\n{Style.BRIGHT}{Fore.CYAN}========= Analysis Summary =========")
for channel, result in Findings.items():
	if result == "No Traffic":
		print(f"{Fore.CYAN}Channel {channel}: {Fore.RED}{result}")
	else:
		print(f"{Fore.CYAN}Channel {channel}: {Fore.GREEN}{result}")
print(f"{Fore.CYAN}====================================")
