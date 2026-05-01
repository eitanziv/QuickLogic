from sigrok.sigrok import Sigrok, ConfigKey
import zipfile
import io

sr = Sigrok()
sr.init()
driver = sr.get_driver('fx2lafw')
driver.init()
devices = driver.scan()
if not devices:
    print("No Devices Found")
else:
    device = devices[0]
    print(f"Found device {device.vendor} {device.model}")

device.open()
print("Device opened successfully")
device.set_config_uint64(ConfigKey.SR_CONF_SAMPLERATE, 8_000_000)
print("Sample rate set")
device.set_config_uint64(ConfigKey.SR_CONF_LIMIT_SAMPLES, 250_000_000)
print("Sample limit set")
device.enable_channels("D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7")
print("Channels enabled")
session = sr.session(devices=device)
print("Session created")
session.start()
print("Capturing...")

### Collect raw data from packets
raw_data = bytearray()
packet_count = 0

while packet_count < 20:
    packet = session.next_packet(timeout=2.0)

    if packet is None:
        print("Timeout - no data received")
        break

    if type(packet).__name__ == "EndPacket":
        print("End of capture")
        break

    if type(packet).__name__ == "LogicPacket":
        raw_data.extend(packet.data)
        if packet.data != b'\xff' * len(packet.data):
            print(f"Non idle data found in packet {packet_count}!")
            print(f"Data: {packet.data[:20]}")
        else:
            print(f"Packet {packet_count}: idle (all 0xFF)")
        packet_count += 1

session.stop()
device.close()
print("Done capturing")

print(f"Total samples collected: {len(raw_data)}")
print(f"First 20 bytes: {bytes(raw_data[:20])}")

### Build the .sr file
metadata = """[global]
sigrok version=0.6.0-git-883c2ac

[device 1]
capturefile=logic-1
total probes=8
samplerate=8 MHz
total analog=0
probe1=D0
probe2=D1
probe3=D2
probe4=D3
probe5=D4
probe6=D5
probe7=D6
probe8=D7
unitsize=1
"""

### Split raw data into 4MB chunks
chunk_size = 4194304
chunks = [raw_data[i:i+chunk_size] for i in range(0, len(raw_data), chunk_size)]

### Write the .sr zip file
output_file = "test_capture.sr"
with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.writestr("version", "2")
    zf.writestr("metadata", metadata)
    for i, chunk in enumerate(chunks, start=1):
        zf.writestr(f"logic-1-{i}", bytes(chunk))

print(f"Capture saved to {output_file} with {len(chunks)} chunks")