import re
import json

# Read PCI IDs file with explicit encoding
with open('usb.ids', 'r', encoding='utf-8') as file:
    lines = file.readlines()

parsed_data = []
vendorObj = {}
deviceList = []
deviceObj = {}
subObj = {}

for line in lines:
    if line.startswith('#'):
        continue
    if len(line) == 1:
        continue
    if not line.startswith('\t'):
        if len(vendorObj) != 0:
            vendorObj['device_list'] = deviceList
            deviceList = []
            parsed_data.append(vendorObj)
            vendorObj = {}
        if len(vendorObj) == 0:
            vendorList = line.split(' ')
            vendorObj['vendor'] = vendorList[0].strip()
            vendorObj['vendor_name'] = ' '.join(vendorList[1:]).strip()
            vendorObj['device_list'] = []
    elif line.startswith('\t\t'):
        subVendorList = line.replace('\t', '').split(' ')
        deviceObj.get('interface').append({
            'interface': subVendorList[0].strip(),
            'interface_name': ' '.join(subVendorList[1:]).strip()
        })
    elif line.startswith('\t'):
        deviceDataList = line.replace('\t', '').split(' ')
        newDeviceData = []
        for i in deviceDataList[:2]:
            if len(i):
                newDeviceData.append(i)
        deviceObj = {
            'device_id': ':'.join(newDeviceData).strip(),
            'device_name': ' '.join(deviceDataList[2:]).strip(),
            'interface': []
        }
        deviceList.append(deviceObj)

# Output parsed data to a JSON file
with open('usb_parsed.json', 'w', encoding='utf-8') as output_file:
    json.dump(parsed_data, output_file, indent=2, ensure_ascii=False)

print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
