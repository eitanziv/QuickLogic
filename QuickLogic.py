import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, metavar="IoT_Capture", help="Name of the saved capture file")
parser.add_argument("--dev", required=True, metavar="tty/USB0", help="Device that will be used for the analysis")
parser.add_argument("--ch", required=True, metavar="0,4,7", help="This is to specify the channels to listen on the logic analyzer (comma separated)")
parser.add_argument("-r", "--rate", type=int, metavar="60000", help="This is to set the rate to something other than default")
arguments = parser.parse_args()

### This will be for grabbing the user defined rate or using the default //NEEDS TO BE UPDATED LATER
if arguments.rate:
    ReadRate = arguments.rate
else:
    ReadRate = 15000

### This takes the input for ch and splits them at the comma and ensures they all fit between 0-7. If not it throws an error
channels = [int(ch.strip()) for ch in arguments.ch.split(",")]
if not all(0 <= ch <= 7 for ch in channels):
    parser.error("Channels must be between 0 and 7")

### Checks for and appends the filename with the .sr file extension if needed
if not arguments.file.endswith(".sr"):
    FileName = arguments.file + ".sr"
else:
    FileName = arguments.file
with open(FileName, "w") as CaptureFile:
    print(f"{arguments.file}\n{arguments.dev}\n{channels}\n{ReadRate}", file=CaptureFile)

print("The File has been created!")
