#!/usr/bin/env python3

import asyncio
from bleak import BleakClient, BleakScanner
import struct
import argparse
import json
import time
import binascii
import atexit
import paho.mqtt.client as paho

import logging

# logging.basicConfig(level=logging.DEBUG)
#
# # Configura il broker MQTT
# broker = "127.0.0.1"
# port = 1883
#
# def on_connect(client, userdata, flags, rc):
#     print(f"Connected with result code {rc}")
#
# def on_disconnect(client, userdata, rc):
#     print(f"Disconnected with result code {rc}")
#
# mqtt = paho.Client("control3")
#
# mqtt.on_connect = on_connect
# mqtt.on_disconnect = on_disconnect
#
# try:
#     mqtt.connect(broker, port, 60)
#     mqtt.loop_start()
# except Exception as e:
#     print(f"Failed to connect to MQTT broker: {e}")


# Command line arguments
parser = argparse.ArgumentParser(description='Fetches and outputs JBD bms data')
parser.add_argument("-b", "--BLEaddress", help="Device BLE Address", required=True)
parser.add_argument("-i", "--interval", type=int, help="Data fetch interval", required=True)
parser.add_argument("-m", "--meter", help="Meter name", required=True)
args = parser.parse_args()
z = args.interval
meter = args.meter

cells1 = []
topic = "data/bms"
gauge = "data/bms/gauge"
broker = "127.0.0.1"
port = 1883

mqtt = None  # Initialize mqtt as a global variable


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")


def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")


def setup_mqtt():
    global mqtt
    mqtt = paho.Client("control3")
    mqtt.on_connect = on_connect
    mqtt.on_disconnect = on_disconnect
    mqtt.connect(broker, port)
    mqtt.loop_start()


setup_mqtt()


def cellinfo1(data):  # process pack info
    infodata = data
    i = 4  # Unpack into variables, skipping header bytes 0-3
    volts, amps, remain, capacity, cycles, mdate, balance1, balance2 = struct.unpack_from('>HhHHHHHH', infodata, i)
    volts = volts / 100
    amps = amps / 100
    capacity = capacity / 100
    remain = remain / 100
    watts = volts * amps  # adding watts field for dbase
    message1 = {
        "meter": "bms",
        "volts": volts,
        "amps": amps,
        "watts": watts,
        "remain": remain,
        "capacity": capacity,
        "cycles": cycles
    }
    ret = mqtt.publish(gauge, payload=json.dumps(message1), qos=0, retain=False)  # not sending mdate (manufacture date)

    bal1 = format(balance1, "b").zfill(16)
    message2 = {
        "meter": "bms",  # using balance1 bits for 16 cells
        "c16": int(bal1[0:1]),
        "c15": int(bal1[1:2]),  # balance2 is for next 17-32 cells - not using
        "c14": int(bal1[2:3]),
        "c13": int(bal1[3:4]),
        "c12": int(bal1[4:5]),  # bit shows (0,1) charging on-off
        "c11": int(bal1[5:6]),
        "c10": int(bal1[6:7]),
        "c09": int(bal1[7:8]),
        "c08": int(bal1[8:9]),
        "c07": int(bal1[9:10]),
        "c06": int(bal1[10:11]),
        "c05": int(bal1[11:12]),
        "c04": int(bal1[12:13]),
        "c03": int(bal1[13:14]),
        "c02": int(bal1[14:15]),
        "c01": int(bal1[15:16])
    }
    ret = mqtt.publish(topic, payload=json.dumps(message2), qos=0, retain=False)


def cellinfo2(data):
    infodata = data
    i = 0  # unpack into variables, ignore end of message byte '77'
    protect, vers, percent, fet, cells, sensors, temp1, temp2, temp3, temp4, b77 = struct.unpack_from('>HBBBBBHHHHB',
                                                                                                      infodata, i)
    temp1 = (temp1 - 2731) / 10
    temp2 = (temp2 - 2731) / 10  # fet 0011 = 3 both on ; 0010 = 2 disch on ; 0001 = 1 chrg on ; 0000 = 0 both off
    temp3 = (temp3 - 2731) / 10
    temp4 = (temp4 - 2731) / 10
    prt = format(protect, "b").zfill(16)  # protect trigger (0,1)(off,on)
    message1 = {
        "meter": "bms",
        "ovp": int(prt[0:1]),  # overvoltage
        "uvp": int(prt[1:2]),  # undervoltage
        "bov": int(prt[2:3]),  # pack overvoltage
        "buv": int(prt[3:4]),  # pack undervoltage
        "cot": int(prt[4:5]),  # current over temp
        "cut": int(prt[5:6]),  # current under temp
        "dot": int(prt[6:7]),  # discharge over temp
        "dut": int(prt[7:8]),  # discharge under temp
        "coc": int(prt[8:9]),  # charge over current
        "duc": int(prt[9:10]),  # discharge under current
        "sc": int(prt[10:11]),  # short circuit
        "ic": int(prt[11:12]),  # ic failure
        "cnf": int(prt[12:13])  # config problem
    }
    ret = mqtt.publish(topic, payload=json.dumps(message1), qos=0, retain=False)

    message2 = {
        "meter": "bms",
        "protect": protect,
        "percent": percent,
        "fet": fet,
        "cells": cells,
        "temp1": temp1,
        "temp2": temp2,
        "temp3": temp3,
        "temp4": temp4
    }
    ret = mqtt.publish(topic, payload=json.dumps(message2), qos=0,
                       retain=False)  # not sending version number or number of temp sensors


def cellvolts1(data):  # process cell voltages
    global cells1
    celldata = data  # Unpack into variables, skipping header bytes 0-3
    i = 4
    cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8 = struct.unpack_from('>HHHHHHHH', celldata, i)
    cells1 = [cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8]  # needed for max, min, delta calculations
    message = {
        "meter": "bms",
        "cell1": cell1,
        "cell2": cell2,
        "cell3": cell3,
        "cell4": cell4,
        "cell5": cell5,
        "cell6": cell6,
        "cell7": cell7,
        "cell8": cell8
    }
    ret = mqtt.publish(gauge, payload=json.dumps(message), qos=0, retain=False)


def cellvolts2(data):  # process cell voltages
    celldata = data
    i = 0  # Unpack into variables, ignore end of message byte '77'
    cell9, cell10, cell11, cell12, cell13, cell14, cell15, cell16, b77 = struct.unpack_from('>HHHHHHHHB', celldata, i)
    message = {
        "meter": "bms",
        "cell9": cell9,
        "cell10": cell10,
        "cell11": cell11,
        "cell12": cell12,
        "cell13": cell13,
        "cell14": cell14,
        "cell15": cell15,
        "cell16": cell16
    }
    ret = mqtt.publish(gauge, payload=json.dumps(message), qos=0, retain=False)

    cells2 = [cell9, cell10, cell11, cell12, cell13, cell14, cell15, cell16]  # adding cells min, max and delta values
    allcells = cells1 + cells2
    cellsmin = min(allcells)
    cellsmax = max(allcells)
    delta = cellsmax - cellsmin
    mincell = (allcells.index(min(allcells)) + 1)  # identify which cell # max and min
    maxcell = (allcells.index(max(allcells)) + 1)
    message1 = {
        "meter": meter,
        "mincell": mincell,
        "cellsmin": cellsmin,
        "maxcell": maxcell,
        "cellsmax": cellsmax,
        "delta": delta
    }
    ret = mqtt.publish(gauge, payload=json.dumps(message1), qos=0, retain=False)


class NotificationHandler:
    def __init__(self):
        pass

    def handleNotification(self, handle, data):
        hex_data = binascii.hexlify(data)  # Given raw bytes, get an ASCII string representing the hex values
        text_string = hex_data.decode('utf-8')
        if text_string.find('dd04') != -1:  # check incoming data for routing to decoding routines
            cellvolts1(data)
        elif text_string.find('dd03') != -1:
            cellinfo1(data)
        elif text_string.find('77') != -1 and len(text_string) == 38:  # x04
            cellvolts2(data)
        elif text_string.find('77') != -1 and len(text_string) == 36:  # x03
            cellinfo2(data)


async def main(address):
    devices = await BleakScanner.discover()
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
        notification_handler = NotificationHandler()
        await client.start_notify("0000ff01-0000-1000-8000-00805f9b34fb", notification_handler.handleNotification)

        while True:
            # Write request to the characteristic to get data
            await client.write_gatt_char("0000ff02-0000-1000-8000-00805f9b34fb", bytearray.fromhex('dda50400fffc77'))
            await asyncio.sleep(5)
            await client.write_gatt_char("0000ff02-0000-1000-8000-00805f9b34fb", bytearray.fromhex('dda50300fffd77'))
            await asyncio.sleep(z)


address = args.BLEaddress
loop = asyncio.get_event_loop()
loop.run_until_complete(main(address))


XdTO-M2UFIcXb5gILC4INYp1hb26zE0bBNeOSpggij9DW2i5FgdENeE0ou87T0BzPUWPSERaqOjWYMLTjnxpfg==