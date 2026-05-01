import argparse
import usb.core
import usb.util
from termcolor import colored
from sigrok.sigrok import Sigrok

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, metavar="IoT_Capture", help="Name of the saved capture file")
parser.add_argument("--ch", required=True, metavar="0,4,7", help="This is to specify the channels to listen on the logic analyzer (comma separated)")
parser.add_argument("-cs", "--speed", type=int, metavar="4000000", help="This is to set the capture speed to something other than default (4000000)")
parser.add_argument("-s", "--size", type=int, metavar="10000000", help="THis is to set the capture size to something other than default (10000000)")
parser.add_argument("--timeout", type=int, metavar="30", help="This will set a timeout value other than the default 15 seconds")
arguments = parser.parse_args()

### This will be for grabbing the user defined capture speed or using the default 
if arguments.speed:
    ReadSpeed = arguments.speed
else:
    ReadSpeed = 4000000

### This will be for grabbing the user defined capture size or using the default
if arguments.size:
    ReadSize = arguments.size
else:
    ReadSize = 10000000

### This is to set the timeout from user input
if arguments.timeout:
    ReadTimeout = arguments.timeout
else:
    ReadTimeout = 15


### function for finding and selecting a USB
## Lookup Table for known logic analyzers
KNOWN_DEVICES = { 
    (0x0925, 0x3881): "Lakeview Research Saleae Logic"
}

device_names = []
devices = []
Selected_Device = None
Selected_Name = None
devices = list(usb.core.find(find_all=True))
if devices is None:
    print("Unable to Identify USBs")
else:
    print("Which Device should we use?")
    for index, USB in enumerate(devices, start=1):
        manufacturer = USB.manufacturer or ""
        product = USB.product or ""
        Check_name = f"{manufacturer} {product}".strip() or "Unknown Device"
        Device_name = KNOWN_DEVICES.get((USB.idVendor, USB.idProduct), Check_name)
        device_names.append(Device_name)
        print(f"{index}: {Device_name} ({USB.idVendor:04x}:{USB.idProduct:04x})")
        
    Analyzer_Choice = int(input("\nSelect the Device: "))
    if 1 <= Analyzer_Choice <= len(devices):
        selection = Analyzer_Choice - 1
        Selected_Device = devices[selection]
        Selected_Name = device_names[selection]
        print(f"\nUsing: {device_names[selection]}")
    else:
        print(f"{colored('Invalid Selection: ', 'red')} Choose a number between 1 and {len(devices)}")

### This takes the input for ch and splits them at the comma and ensures they all fit between 0-7. If not it throws an error
channels = [int(ch.strip()) for ch in arguments.ch.split(",")]
if not all(0 <= ch <= 7 for ch in channels):
    parser.error("Channels must be between 0 and 7")

### Checks for and appends the filename with the .sr file extension if needed
# if not arguments.file.endswith(".sr"):
#     FileName = arguments.file + ".sr"
# else:
#     FileName = arguments.file
# with open(FileName, "w") as CaptureFile:
#     print(f"{arguments.file}\n{channels}\n{ReadRate}", file=CaptureFile)

# print("The File has been created!")


### This will begin the implementation of the Sigrok bindings
# Context = Sigrok()
# driver = Context.drivers['fx2lafw']
# print(dir(driver))
