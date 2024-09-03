# import struct
#
# data = bytearray(b'\xdd\x03\x00&\x12.\x00\x00\x02A\x07\x80\x00\x01/I\x00\x00\x00\x00\x00\x008\x1e\x03\r\x03\x0b\xd4\x0b\xc7\x0b\xc3\x00\x00\x00\x07\x80\x02A\x00\x00\xfa\xa5w')
# current_bytes = data[6:8]
#
# current_value = struct.unpack('>H', current_bytes)[0]
#
# print(f'Raw current value: {current_value}')
# print(f'Current in mA: {current_value} mA')
import json
import matplotlib.pyplot as plt

def normalizza(lista):
    minimo = min(lista)
    massimo = max(lista)
    return [(x - minimo) / (massimo - minimo) for x in lista]

with open(r"/Users/liviobasile/Downloads/bms-main/service/bms_data_log.json", "r") as f:
    data = json.load(f)
    print(data['general_data'][10][1])
    print(data['general_data'][12][1])
    print(data['general_data'][13][1])
    #print(data)
    data_7 = []
    data_6 = []
    try_current = []
    for elem in data['general_data']:
        #print(elem[1])
        data = elem[1]
        # print("_" * 30)
        # print(data[6])
        # print(data[7])
        data_7.append(data[7])
        data_6.append(data[6])
        print((data[6] * 256 + data[7]) / 100)
        try_current.append((data[6] + data[7]) / 100)
        # print("_"*30)

with open(r"/Users/liviobasile/Downloads/bms-main/service/bms_data.json", "r") as f:
    data = json.load(f)
    plt.plot(normalizza(data["Total Volts"]), label="Volts")
    #plt.plot(normalizza(data_7), label='Current')
    plt.plot(normalizza(try_current), label='Current')

    plt.title('Grafico dei valori')

    plt.xlabel('Measurement')
    plt.ylabel('Volts')
#


#plt.show()