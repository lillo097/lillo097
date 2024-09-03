import asyncio
import json
import os
from bleak import BleakClient
import struct
from datetime import datetime

# Constants
DEVICE_ADDRESS = "4B096330-7B3C-07A0-4D05-3E751E55D587"
BMS_SERVICE_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"
BMS_RX_CHAR_UUID = "0000ff01-0000-1000-8000-00805f9b34fb"
BMS_TX_CHAR_UUID = "0000ff02-0000-1000-8000-00805f9b34fb"

# Globals
bms_data_received = bytearray()
bms_data_length_received = 0
bms_data_length_expected = 0
bms_data_error = False
interaction_timing = 1

data_corrente = datetime.now()
data_formattata = data_corrente.strftime("%d-%m-%Y")

JSON_FILE_PATH_1 = f'bms_data_(for-general-parameters)_{data_formattata}.json'
JSON_FILE_PATH_2 = f'bms_data_log_(for-current-parameters)_{data_formattata}.json'

def save_to_json(data, file_path=JSON_FILE_PATH_1):
    """Appends data to a JSON file, maintaining lists for each parameter."""
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            try:
                existing_data = json.load(file)
                if not isinstance(existing_data, dict):
                    existing_data = {}
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    # Append new data to existing data
    for key, value in data.items():
        if key not in existing_data:
            existing_data[key] = []
        existing_data[key].append(value)

    # Save updated data to file
    with open(file_path, "w") as file:
        json.dump(existing_data, file, indent=4)


def append_bms_packet(data):
    """Appends data to the global received data buffer."""
    global bms_data_received, bms_data_length_received, bms_data_error

    if len(data) + bms_data_length_received >= 100:
        return False

    bms_data_received.extend(data)
    bms_data_length_received += len(data)
    return True

def get_checksum_for_received_data(data):
    """Calculates the checksum for the received data."""
    checksum = 0x10000
    data_length_provided = data[3]

    for i in range(data_length_provided + 1):
        checksum -= data[i + 3]

    return checksum

def get_is_checksum_valid_for_received_data(data):
    """Validates the checksum for the received data."""
    checksum_index = data[3] + 4
    checksum_received = data[checksum_index] * 256 + data[checksum_index + 1]
    return get_checksum_for_received_data(data) == checksum_received


# Initialize persistent storage
bms_data_log = {
    "general_data": [],
    "cell_data": []
}

def format_bms_data_received(data, bms_data_log):
    """Formats the BMS data received into a dictionary with lists for each parameter."""
    bms_data = {}

    if data[1] == 0x03:
        print(f"data general: {data}")
        #______________________________________
        current_bytes = data[6:8]

        # Decode the bytes as an unsigned short (2 bytes)
        current_value = struct.unpack('>H', current_bytes)[0]

        # Print the current value in raw form and converted to mA
        print(f'Raw current value: {current_value}')
        print(f'Current in mA: {current_value} mA')
        # ______________________________________

        bms_data["Total Volts"] = ((data[4] * 256 + data[5]) / 100)
        bms_data["Current"] = ((data[6] * 256 + data[7]) / 100)
        bms_data["Remaining Capacity"] = (data[8] * 256 + data[9]) / 100
        # bms_data["Nominal Capacity"] = (data[10] * 256 + data[11]) / 100
        # bms_data["Total Cycles"] = data[12] * 256 + data[13]
        date = data[14] * 256 + data[15]
        # bms_data["Production Date"] = f"{((date >> 9) + 2000)}/{((date >> 5) & 0x0F)}/{date & 0x1F}"

        # bms_data["Cell Balancing"] = [
        #     "balancing" if (data[16 + i // 8] >> (7 - i % 8) & 0x01) == 1 else "not balancing"
        #     for i in range(data[25])
        # ]

        # protection_status = data[20] * 256 + data[21]
        # bms_data["Protection Status"] = ''.join(str((protection_status >> i) & 0x01) for i in reversed(range(16)))

        # bms_data["Software Version"] = data[22] / 10
        bms_data["Remaining Percent (SOC)"] = data[23]
        # bms_data["MOSFET State"] = {
        #     "Charge": "ON" if (data[24] & 0x01) == 1 else "OFF",
        #     "Discharge": "ON" if (data[24] & 0x02) == 2 else "OFF"
        # }
        # bms_data["Number of Battery Strings"] = data[25]

        number_of_temperature_sensors = data[26]
        bms_data["Temperature Sensors"] = {
            f"T{i}": (data[27 + i * 2] * 256 + data[28 + i * 2] - 2731) / 10
            for i in range(number_of_temperature_sensors)
        }

        # Append the general data to the log
        bms_data_log["general_data"].append([str(data), [elem for elem in data]])

    elif data[1] == 0x04:
        bms_number_of_cells = data[3] // 2
        bms_data["Cell Voltages"] = [
            data[4 + 2 * i] * 256 + data[5 + 2 * i]
            for i in range(bms_number_of_cells)
        ]

        print(f"data cells: {data}")

        # Append the cell data to the log
        bms_data_log["cell_data"].append([str(data), [elem for elem in data]])

    # Save the accumulated data to a JSON file
    with open(JSON_FILE_PATH_2, 'w') as json_file:
        json.dump(bms_data_log, json_file, indent=4)

    return bms_data

# Example usage:
# data = ...  # some byte array received from the BMS
# format_bms_data_received(data, bms_data_log)

async def notification_handler(characteristic, data):
    """Handles incoming notifications from the BMS device."""
    global bms_data_received, bms_data_length_received, bms_data_length_expected, bms_data_error

    if bms_data_error:
        return

    # If new data is received
    if bms_data_length_received == 0:
        if data[0] == 0xDD:
            bms_data_error = data[2] != 0
            bms_data_length_expected = data[3]
            if not bms_data_error:
                bms_data_error = not append_bms_packet(data)
    else:
        bms_data_error = not append_bms_packet(data)

    if not bms_data_error:
        if bms_data_length_received >= bms_data_length_expected + 7:
            if get_is_checksum_valid_for_received_data(bms_data_received):
                formatted_data = format_bms_data_received(bms_data_received, bms_data_log)
                save_to_json(formatted_data)
                bms_data_received.clear()
                bms_data_length_received = 0
                bms_data_length_expected = 0
            else:
                bms_data_received.clear()
                bms_data_length_received = 0
                bms_data_length_expected = 0


async def run_client():
    """Runs the BLE client to interact with the BMS device."""
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connected: {client.is_connected}")

        def handle_disconnect(client):
            print("Disconnected")

        client.on_disconnect = handle_disconnect

        await client.start_notify(BMS_RX_CHAR_UUID, notification_handler)

        while True:
            current_time = int(asyncio.get_event_loop().time())
            if client.is_connected:
                if current_time % 2 == 0:
                    data = bytearray([0xDD, 0xA5, 0x03, 0x00, 0xFF, 0xFD, 0x77])
                else:
                    data = bytearray([0xDD, 0xA5, 0x04, 0x00, 0xFF, 0xFC, 0x77])

                await client.write_gatt_char(BMS_TX_CHAR_UUID, data)
                global bms_data_length_received, bms_data_length_expected, bms_data_error
                bms_data_length_received = 0
                bms_data_length_expected = 0
                bms_data_error = False

            await asyncio.sleep(interaction_timing)


if __name__ == "__main__":
    asyncio.run(run_client())
