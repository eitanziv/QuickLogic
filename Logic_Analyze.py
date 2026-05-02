import zipfile
import sys



##Grabs .sr file anc checks magic bytes to see if it is a correct zip
Capture_File = "test_capture.sr"

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
	with open("bytes.txt", "wb") as byte_file:  ## This needs to be removed in function version since everything will be in memory
		byte_file.write(raw_data)

## This section performs a check for each channel to see if the channel idles high or low indicating no traffic and adds the active channels to an array
channels = [0, 1, 2, 3, 4, 5, 6, 7]
channel_data = {}
active_channels = []

for channel in channels:
	bits = []
	for byte in raw_data:
		bit = (byte >> channel) & 1
		bits.append(bit)
	channel_data[channel] = bits

for channel, bits in channel_data.items():
	if len(set(bits)) == 1:
		print(f"Nothing going on at channel {channel}")
	else:
		active_channels.append(channel)
		print(f"Active channel on channel {channel}")

## Beginning of the analysis functions






## This is a list of common baud rates to check. Future versions will offer an option to calculate the baud if these do not work.
##Common_Bauds = [115200, 9600, 38400, 57600, 19200, 4800]
