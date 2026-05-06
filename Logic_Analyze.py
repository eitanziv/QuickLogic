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
	samples_per_bit = round(SAMPLE_RATE / COMMON_BAUDS[0])
	signal_start = bits.index(0)
	signal_stagger = round(samples_per_bit / 2)
	decoded_data = ""
	binary_data = []
	full_bytes = []
	bytes_collected = 0

## This gets a sample to test for ascii percentage before fully commiting the entire capture to decode
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
	if len(set(bits)) == 1:
		print(f"Nothing going on at channel {channel}")
	else:
		active_CHANNELS.append(channel)
		print(f"Active channel on channel {channel}")

print(UART_Check(channel_data[0], SAMPLE_RATE, Capture_File))