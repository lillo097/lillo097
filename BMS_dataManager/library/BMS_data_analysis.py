##
import matplotlib.pyplot as plt
import json

def normalize_list(input_list):
    if not input_list:
        return []

    min_val = min(input_list)
    max_val = max(input_list)

    # Handle the case where all values in the list are the same
    if min_val == max_val:
        return [0.0] * len(input_list)

    return [(x - min_val) / (max_val - min_val) for x in input_list]

def combine_hex_strings(hex_str1, hex_str2):
    hex_str1 = hex_str1.lower()
    hex_str2 = hex_str2.lower()

    combined_hex_str = hex_str1 + hex_str2

    combined_int = int(combined_hex_str, 16)

    hex_16bit_str = f"0x{combined_int:04X}"

    return hex_16bit_str, combined_int

with open(r"/Users/liviobasile/Downloads/bms-main/service/bms_data_log_2.json", "r") as f:
    data = json.load(f)
    current = []
    for elem in data['general_data']:
        hex_string = eval(elem[0]).hex()

        sub_hex_string = hex_string[12:16]

        hex_result, decimal_result = combine_hex_strings(sub_hex_string[0:2], sub_hex_string[2:4])
        print(f"Hexadecimal: {hex_result}")
        if hex_result == '0x0000':
            current_value = int(0)
            print(f"Decimal: {0}")  # Output: 65287
            current.append(current_value)
        else:
            current_value = (65536 - int(decimal_result)) / 100
            current.append(current_value)
            print(f"Decimal: {(65536 - int(decimal_result)) / 100}")

print(current)

with open(r"/Users/liviobasile/Downloads/bms-main/service/bms_data_2.json", 'r') as f:
    data = json.load(f)

#plt.plot(normalize_list(current))
#plt.plot(current)
normalized_current = normalize_list(current)
normalized_total_volts = normalize_list(data['Total Volts'])
normalized_remaining_capacity = normalize_list(data["Remaining Capacity"])

# Plot with legend
plt.figure(figsize=(30, 12))
plt.plot(normalized_current, marker='o', linestyle='-', color='b', label='Current')
plt.plot(normalized_total_volts, marker='o', linestyle='-', color='r', label='Total Volts')
plt.plot(normalized_remaining_capacity, marker='o', linestyle='-', color='g', label='Remaining Capacity')

#Annotate the current values with real values
for i, (norm_value, real_value) in enumerate(zip(normalized_current, current)):
    plt.text(i, norm_value, f'{real_value:.2f}', ha='center', va='bottom',
             bbox=dict(facecolor='white', edgecolor='blue', boxstyle='round,pad=0.3'))

# Annotate the Total Volts values with real values
for i, (norm_value, real_value) in enumerate(zip(normalized_total_volts, data['Total Volts'])):
    plt.text(i, norm_value, f'{real_value:.2f}', ha='center', va='top',
             bbox=dict(facecolor='white', edgecolor='red', boxstyle='round,pad=0.3'))

# Annotate the Remaining Capacity values with real values
for i, (norm_value, real_value) in enumerate(zip(normalized_remaining_capacity, data["Remaining Capacity"])):
    plt.text(i, norm_value, f'{real_value:.2f}', ha='center', va='top',
             bbox=dict(facecolor='white', edgecolor='green', boxstyle='round,pad=0.3'))

# Adding the legend
plt.legend()

# Labels, title, and grid
plt.title('Plot with Annotations Showing Real Values')
plt.xlabel('Index')
plt.ylabel('Normalized Value')
plt.grid(True)
plt.show()
##
import matplotlib.pyplot as plt
with open(r"/Users/liviobasile/Downloads/bms-main/service/bms_data_1.json", 'r') as f:
    data = json.load(f)

print(data["Cell Voltages"])

# Merging by columns
merged_columns = [list(column) for column in zip(*data["Cell Voltages"])]

plt.figure(figsize=(30, 12))

for i, row in enumerate(merged_columns):
    plt.plot(row, marker='o', linestyle='-', label=f'Cell_{i + 1}')

    # Annotate each point with its value
    for j, value in enumerate(row):
        plt.text(j, value, f'{value}', ha='center', va='bottom',
                 bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

# Adding labels and title
plt.title('Plot of All Cells')
plt.xlabel('Index')
plt.ylabel('Value')
plt.grid(True)

# Adding a legend
plt.legend()

# Display the plot
plt.show()







