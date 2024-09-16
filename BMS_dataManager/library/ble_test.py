import asyncio
from bleak import BleakClient, BleakScanner

# Define the UUIDs for the services and characteristics
BMS_SERVICE_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"
BMS_TX_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"
BMS_RX_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"

# Function to handle received data
def handle_notification(characteristic, data):
    print(f"Received notification from {characteristic.uuid}: {data.hex()}")

    # Process the received data
    if data[0] == 0xDD:
        if data[1] == 0x03:
            print("Overall data received:")
            print_data_overall(data)
        elif data[1] == 0x04:
            print("Cell data received:")
            print_data_cells(data)

def print_data_overall(data):
    print(f"Total Volts: {((data[4] * 256 + data[5]) / 100):.2f}V") #ok
    print(f"Current: {((data[6] * 256 + data[7]) / 100):.2f}A") #ok
    print(f"Remaining Capacity: {((data[8] * 256 + data[9]) / 100):.2f}Ah") #ok
    print(f"Nominal Capacity: {((data[10] * 256 + data[11]) / 100):.2f}Ah") #ok
    print(f"Total cycles: {data[12] * 256 + data[13]}") #ok
    date = data[14] * 256 + data[15]
    print(f"Production date YYYY/MM/DD: {((date >> 9) + 2000)}/{((date >> 5) & 0x0F)}/{date & 0x1F}") #ok

    # print("data", data)
    #
    # for i in range(0, 31):
    #     try:
    #         # Try to access and print the element at index i
    #         print(f"data[{i}] = {data[i]}")
    #     except IndexError:
    #         # Handle the case where the index is out of range
    #         print(f"data[{i}] = Index out of range")

    # print(f"Number of cells: {data[25]}")
    # for i in range(data[25]):
    #     b = data[16 + i // 8]
    #     shift = 7 - i % 8
    #     print(f"Cell {i + 1} {'balancing' if (b >> shift) & 0x01 else 'not balancing'}")

    # protection_status = data[20] * 256 + data[21]
    # print(f"Protection status: {''.join(str((protection_status >> i) & 0x01) for i in range(15, -1, -1))}")

    #print(f"Software version: {data[22] / 10:.1f}")

    #print(f"Remaining percent (SOC): {data[23]}%")

    #print(f"MOSFET state: charge {'ON' if data[24] & 0x01 else 'OFF'}, discharge {'ON' if data[24] & 0x02 else 'OFF'}")

    #print(f"Number of battery strings: {data[25]}")

    #number_of_temp_sensors = data[26]
    #print(f"Number of temperature sensors: {number_of_temp_sensors}")

    # for i in range(number_of_temp_sensors):
    #     temperature = ((data[27 + i * 2] * 256 + data[28 + i * 2] - 2731)) / 10
    #     print(f"Temperature sensor {i + 1}: {temperature:.1f}C")

def print_data_cells(data):
    number_of_cells = data[3] // 2
    print(number_of_cells)
    for i in range(number_of_cells):
        millivolts = data[4 + 2 * i] * 256 + data[5 + 2 * i]
        #print("millivolts", data)
        print(f"Cell {i + 1}: {millivolts / 1000:.3f}V")

async def run():
    # Discover devices
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")

    # Connect to the device
    address = "4B096330-7B3C-07A0-4D05-3E751E55D587"  # Replace with your device's address
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")

        # Subscribe to notifications
        await client.start_notify(BMS_RX_UUID, handle_notification)

        ticker = 0
        while True:
            await asyncio.sleep(5)
            ticker += 1
            print(f"Tick {ticker:03d}: ", end="")
            if client.is_connected:
                if ticker % 2 == 0:
                    print("Requesting overall data")
                    data = bytearray([0xDD, 0xA5, 0x03, 0x00, 0xFF, 0xFD, 0x77])
                else:
                    print("Requesting cell data")
                    data = bytearray([0xDD, 0xA5, 0x04, 0x00, 0xFF, 0xFC, 0x77])
                await client.write_gatt_char(BMS_TX_UUID, data)
            else:
                print("Not connected")

asyncio.run(run())

