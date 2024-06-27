from diet_functions import *
import configparser
import os

config_file = "../config.properties"
config = configparser.ConfigParser()
config.read(config_file)

file_path_DB = config.get('Paths', 'file_path_DB')
file_path_xlsx = config.get('Paths', 'file_path')

DB = config.get('General', 'DB')
day = config.get('General', 'day')
save_xlsx = config.get('General', 'save_xlsx')
P_min = int(config.get('Parameters', 'P_min'))
P_max = int(config.get('Parameters', 'P_max'))
F_min = int(config.get('Parameters', 'F_min'))
F_max = int(config.get('Parameters', 'F_max'))
C_min = int(config.get('Parameters', 'C_min'))
C_max = int(config.get('Parameters', 'C_max'))
cal_min = int(config.get('Parameters', 'cal_min'))
cal_max = int(config.get('Parameters', 'cal_max'))

file_path_diet = os.path.join(
    os.path.dirname(file_path_DB),
    f"diet_calculator_{cal_max}kcal.xlsx"
)

if save_xlsx == "True":
    sorted_alimenti_min, sorted_alimenti_max, final_daily_dict, dizionario_alimenti_min, dizionario_alimenti_max = process_food_data(file_path_DB, file_path_diet, DB, day)
    alimenti = final_daily_dict
    peso_min_alimenti = dizionario_alimenti_min  # g di alimento minimo
    peso_max_alimenti = dizionario_alimenti_max # g di alimento massimo
    df_al, proteine_tot, grassi_tot, carboidrati_tot, calorie_tot, problema = pianificazione_pasti(alimenti, P_min, P_max, F_min, F_max, C_min, C_max, cal_min, cal_max, peso_min_alimenti, peso_max_alimenti, sorted_alimenti_min, sorted_alimenti_max)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Stato:", LpStatus[problema.status])
    df_al[' Violed'] = df_al.apply(check_range, axis=1)
    print(df_al)
    create_excel(day, df_al, cal_max, proteine_tot, grassi_tot, carboidrati_tot, calorie_tot, file_path_xlsx)
else:
    sorted_alimenti_min, sorted_alimenti_max, final_daily_dict, dizionario_alimenti_min, dizionario_alimenti_max = process_food_data(file_path_DB, file_path_diet, DB, day)
    alimenti = final_daily_dict
    peso_min_alimenti = dizionario_alimenti_min  # g di alimento minimo
    peso_max_alimenti = dizionario_alimenti_max # g di alimento massimo
    df_al, proteine_tot, grassi_tot, carboidrati_tot, calorie_tot, problema = pianificazione_pasti(alimenti, P_min, P_max, F_min, F_max, C_min, C_max, cal_min, cal_max, peso_min_alimenti, peso_max_alimenti, sorted_alimenti_min, sorted_alimenti_max)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Stato:", LpStatus[problema.status])
    df_al[' Violed'] = df_al.apply(check_range, axis=1)
    print(df_al)

print("\n")
print("Apporto proteico totale:", round(value(proteine_tot),1), f"g (range: {P_min} <-> {P_max})")
print("Apporto di grassi totale:", round(value(grassi_tot),1), f"g (range: {F_min} <-> {F_max})")
print("Apporto di carboidrati totale:", round(value(carboidrati_tot),1), f"g (range: {C_min} <-> {C_max})")
print("Apporto di calorie totale:", round(value(calorie_tot),1), f"kcal (range: {cal_min} <-> {cal_max})")
print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")