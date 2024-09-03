##
import asyncio
from bleak import BleakScanner, BleakClient

async def get_device_info(device):
    device_info = {
        "Name": device.name,
        "Address": device.address,
        "RSSI": device.rssi,
        "Details": device.details,
        "Metadata": device.metadata,
        "Services": []
    }

    async with BleakClient(device) as client:
        services = await client.get_services()
        for service in services:
            service_info = {
                "UUID": service.uuid,
                "Characteristics": []
            }
            for characteristic in service.characteristics:
                characteristic_info = {
                    "UUID": characteristic.uuid,
                    "Properties": characteristic.properties,
                    "Descriptors": []
                }
                for descriptor in characteristic.descriptors:
                    characteristic_info["Descriptors"].append(descriptor.uuid)
                service_info["Characteristics"].append(characteristic_info)
            device_info["Services"].append(service_info)
    return device_info

async def run():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Scanning device: {device.name}")
        device_info = await get_device_info(device)
        print(device_info)
        print("-" * 30)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())




##
import asyncio
from bleak import BleakClient

address = "8F88A71E-1DDC-64F6-9DEC-9DB1CEA476DD"
characteristic_uuid = "4E3000A2-A2BB-DC65-33C2-E43536BCCB9E"


async def notification_handler(sender, data):
    print(f"Notification from {sender}: {data}")


async def main():
    print("Attempting to connect to the device...")
    async with BleakClient(address) as client:
        connected = await client.is_connected()
        print(f"Connected: {connected}")

        if not connected:
            print("Failed to connect to the device.")
            return

        print(f"Subscribing to characteristic {characteristic_uuid} for notifications...")
        try:
            await client.start_notify(characteristic_uuid, notification_handler)
            print(f"Successfully subscribed to notifications for {characteristic_uuid}.")
            await asyncio.sleep(30)  # Listen for notifications for 30 seconds
            await client.stop_notify(characteristic_uuid)
            print(f"Unsubscribed from notifications for {characteristic_uuid}.")
        except Exception as e:
            print(f"Failed to subscribe to characteristic {characteristic_uuid}: {e}")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

#


##
import asyncio
from bleak import BleakClient, BleakScanner
import struct
import binascii
import argparse
import time

# Command line arguments
parser = argparse.ArgumentParser(description='Fetches and outputs JBD BMS data')
parser.add_argument("-a", "--address", help="Device BLE Address", required=True)
parser.add_argument("-i", "--interval", type=int, help="Data fetch interval", required=True)
parser.add_argument("-m", "--meter", help="Meter name", required=True)
args = parser.parse_args()
z = args.interval
meter = args.meter

cells1 = []

def handle_notification(sender, data):
    hex_data = binascii.hexlify(data)
    text_string = hex_data.decode('utf-8')
    print("data:", data)
    volts, amps, remain, capacity, cycles, mdate, balance1, balance2 = struct.unpack_from('>HhHHHHHH', data, 4)
    print(amps /= 100)
    if text_string.find('dda5') != -1 and text_string[6:8] == '03':
        cellinfo1(data)
    elif text_string.find('dda5') != -1 and text_string[6:8] == '04':
        cellvolts1(data)
    elif text_string.find('77') != -1 and len(text_string) == 38:
        cellvolts2(data)
    elif text_string.find('77') != -1 and len(text_string) == 36:
        cellinfo2(data)

def cellinfo1(data):
    i = 4
    volts, amps, remain, capacity, cycles, mdate, balance1, balance2 = struct.unpack_from('>HhHHHHHH', data, i)
    volts /= 100
    amps /= 100
    capacity /= 100
    remain /= 100
    watts = volts * amps
    bal1 = (format(balance1, "b").zfill(16))
    c16 = int(bal1[0:1])
    c15 = int(bal1[1:2])
    c14 = int(bal1[2:3])
    c13 = int(bal1[3:4])
    c12 = int(bal1[4:5])
    c11 = int(bal1[5:6])
    c10 = int(bal1[6:7])
    c09 = int(bal1[7:8])
    c08 = int(bal1[8:9])
    c07 = int(bal1[9:10])
    c06 = int(bal1[10:11])
    c05 = int(bal1[11:12])
    c04 = int(bal1[12:13])
    c03 = int(bal1[13:14])
    c02 = int(bal1[14:15])
    c01 = int(bal1[15:16])
    message = f"meter,volts,amps,watts,remain,capacity,cycles\r\n{meter},{volts:.2f},{amps:.2f},{watts:.2f},{remain},{capacity},{cycles}"
    print(message)
    message = f"meter,c01,c02,c03,c04,c05,c06,c07,c08\r\n{meter},{c01},{c02},{c03},{c04},{c05},{c06},{c07},{c08}"
    print(message)
    message = f"meter,c09,c10,c11,c12,c13,c14,c15,c16\r\n{meter},{c09},{c10},{c11},{c12},{c13},{c14},{c15},{c16}"
    print(message)
    print('___________________________________________________________________________')

def cellinfo2(data):
    i = 0
    protect, vers, percent, fet, cells, sensors, temp1, temp2, temp3, temp4, b77 = struct.unpack_from('>HBBBBBHHHHB', data, i)
    temp1 = (temp1 - 2731) / 10
    temp2 = (temp2 - 2731) / 10
    temp3 = (temp3 - 2731) / 10
    temp4 = (temp4 - 2731) / 10
    prt = (format(protect, "b").zfill(16))
    ovp = int(prt[0:1])
    uvp = int(prt[1:2])
    bov = int(prt[2:3])
    buv = int(prt[3:4])
    cot = int(prt[4:5])
    cut = int(prt[5:6])
    dot = int(prt[6:7])
    dut = int(prt[7:8])
    coc = int(prt[8:9])
    duc = int(prt[9:10])
    sc = int(prt[10:11])
    ic = int(prt[11:12])
    cnf = int(prt[12:13])
    message = f"meter,ovp,uvp,bov,buv,cot,cut,dot,dut,coc,duc,sc,ic,cnf\r\n{meter},{ovp},{uvp},{bov},{buv},{cot},{cut},{dot},{dut},{coc},{duc},{sc},{ic},{cnf}"
    print(message)
    message = f"meter,protect,percent,fet,cells,temp1,temp2,temp3,temp4\r\n{meter},{protect:0000},{percent:00},{fet:00},{cells},{temp1:.1f},{temp2:.1f},{temp3:.1f},{temp4:.1f}"
    print(message)

def cellvolts1(data):
    global cells1
    i = 4
    cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8 = struct.unpack_from('>HHHHHHHH', data, i)
    cells1 = [cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8]
    message = f"meter,cell1,cell2,cell3,cell4,cell5,cell6,cell7,cell8\r\n{meter},{cell1},{cell2},{cell3},{cell4},{cell5},{cell6},{cell7},{cell8}"
    print(message)

def cellvolts2(data):
    global cells1
    i = 0
    cell9, cell10, cell11, cell12, cell13, cell14, cell15, cell16, b77 = struct.unpack_from('>HHHHHHHHB', data, i)
    message = f"meter,cell9,cell10,cell11,cell12,cell13,cell14,cell15,cell16\r\n{meter},{cell9},{cell10},{cell11},{cell12},{cell13},{cell14},{cell15},{cell16}"
    print(message)
    cells2 = [cell9, cell10, cell11, cell12, cell13, cell14, cell15, cell16]
    cells = cells1 + cells2
    mincell = min(cells)
    maxcell = max(cells)
    delta = maxcell - mincell
    minindex = cells.index(mincell) + 1
    maxindex = cells.index(maxcell) + 1
    message = f"meter,mincell,cellsmin,maxcell,cellsmax,delta\r\n{meter},cell{minindex},{mincell},cell{maxindex},{maxcell},{delta}"
    print(message)

async def main(address):
    scanner = BleakScanner()
    devices = await scanner.discover()
    target = None
    for device in devices:
        if device.address == address:
            print(f"Found target device: {device.name} with address: {device.address}")
            target = device
            break

    if target is None:
        print("Device not found!")
        return

    async with BleakClient(target) as client:
        print(f"Connected to {target.name}")
        services = await client.get_services()
        for service in services:
            print(f"Service: {service.uuid}")
            for characteristic in service.characteristics:
                print(f"  Characteristic: {characteristic.uuid} - {characteristic.properties}")
                if "notify" in characteristic.properties:
                    await client.start_notify(characteristic.uuid, handle_notification)

        while True:
            write_characteristic = '0000ff02-0000-1000-8000-00805f9b34fb'
            await client.write_gatt_char(write_characteristic, bytearray.fromhex('dda50300fffd77'))
            await asyncio.sleep(z)
            await client.write_gatt_char(write_characteristic, bytearray.fromhex('dda50400fffc77'))
            await asyncio.sleep(z)

address = args.address
loop = asyncio.get_event_loop()
loop.run_until_complete(main(address))

