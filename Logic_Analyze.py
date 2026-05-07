import zipfile
import sys

COMMON_BAUDS = [115200, 9600, 38400, 57600, 19200, 4800]
SAMPLE_RATE = 8_000_000
CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7]
Capture_File = "test_capture.sr"
channel_data = {}
active_CHANNELS = []

## This is the list of functions
## Check for UART function
def UART_Check (bits, SAMPLE_RATE, Capture_File):
## This gets a sample to test for ascii percentage before fully commiting the entire capture to decode
	
	for baud in COMMON_BAUDS:
		samples_per_bit = round(SAMPLE_RATE / baud)
		signal_stagger = round(samples_per_bit / 2)
		signal_start = bits.index(0)
		decoded_data = ""
		binary_data = []
		bytes_collected = 0
		while bytes_collected < 100:
			data_start = signal_start + samples_per_bit + signal_stagger

			for b in range(8):
				position  = data_start + (b * samples_per_bit)
				binary_data.append(bits[position])

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
		
		if print_percent * 100 >= 85:
			print(f"We got a match of {print_percent:.0%} at {baud}")
			print(decoded_data)
			while True:
				response = input("A positive match was found! Would you like to print the decoded version to a file? (y/n): ").lower().strip()
				if response in ['y', 'yes']:
					print("Decoding...")
					break
				elif response in ['n', 'no']:
					print("Exiting...")
					break
				else:
					print("Invalid response please enter 'y' or 'n'.")
			break


	return decoded_data
##Grabs .sr file anc checks magic bytes to see if it is a correct zip THIS WILL BE CHANGED AND WILL BE FROM THE COMMANDS PARAMETERS
if zipfile.is_zipfile(Capture_File):
	print("Lets get diggin!")
else:
	print("Issues reading capture file please check!")
	sys.exit()

## reads .sr file and grabs the logic files that will be analyzed
raw_data = bytearray()

with zipfile.ZipFile(Capture_File, 'r') as capture:
	files = capture.namelist()
	df = [f for f in files if f.startswith("logic-1")]
	print(df)

## breaks down the logic files into one byte array
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

for channel, bits in channel_data.items():
	if len(set(bits)) != 1:
		active_CHANNELS.append(channel)
		print(f"Active channel on channel {channel}")

UART_Check(channel_data[0], SAMPLE_RATE, Capture_File)

