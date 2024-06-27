import pandas as pd

data = pd.read_csv('/Users/liviobasile/Downloads/Diet_builder/dataframe.csv')

meals = {
    "colazione": [
        "albume",
        "yogurt 0% bianco",
        "farina (normale)",
        "sciroppo acero",
        "uova"
    ],
    "spuntino_1": [
        "wasa",
        "bresaola"
    ],
    "pranzo": [
        "barilla lenticchie",
        "stracchino",
        "insalata",
        "olio"
    ],
    "spuntino_2": [
        "proteine buone"
    ],
    "cena": [
        "fettine vitello",
        "riso",
        "cavolfiore"
    ],
    "spuntino_3": [
        "Milk pro budino (20g)"
    ]
}


d_ordered = {}
for alimento in data["Alimento"]:
    for meal in meals:
        if alimento in meals[meal]:
            d_ordered[meal] =  meals[meal]

print(d_ordered)