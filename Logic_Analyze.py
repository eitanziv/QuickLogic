import zipfile
import sys



##Grabs .sr file anc checks magic bytes to see if it is a correct zip
Capture_File = "test_capture.sr"

if zipfile.is_zipfile(Capture_File):
	print("Lets get diggin!")
else:
	print("Issues reading capture file please check!")
	sys.exit()


with zipfile.ZipFile(Capture_File, 'r') as capture:
	files = capture.namelist()
	df = [f for f in files if f.startswith("logic-1")]
	print(df)








## This is a list of common baud rates to check. Future versions will offer an option to calculate the baud if these do not work.
##Common_Bauds = [115200, 9600, 38400, 57600, 19200, 4800]
