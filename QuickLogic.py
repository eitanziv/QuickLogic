import argparse
import usb.core
import usb.util
from termcolor import colored

parser = argparse.ArgumentParser()
parser.add_argument("--file", required=True, metavar="IoT_Capture", help="Name of the saved capture file")
parser.add_argument("--ch", required=True, metavar="0,4,7", help="This is to specify the channels to listen on the logic analyzer (comma separated)")
parser.add_argument("-r", "--rate", type=int, metavar="60000", help="This is to set the rate to something other than default")
arguments = parser.parse_args()

### function for finding and selecting a usb
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

print(f"{Selected_Device.manufacturer} {Selected_Device.Product}:{Selected_Name}")
    
        


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
# if not arguments.file.endswith(".sr"):
#     FileName = arguments.file + ".sr"
# else:
#     FileName = arguments.file
# with open(FileName, "w") as CaptureFile:
#     print(f"{arguments.file}\n{channels}\n{ReadRate}", file=CaptureFile)

# print("The File has been created!")
