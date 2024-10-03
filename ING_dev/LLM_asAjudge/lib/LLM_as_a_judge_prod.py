import vertexai
from vertexai.preview.generative_models import GenerativeModel
import os
import pandas as pd

PROJECT_ID = "i-hsvf-hxchi29m-5kfcbd03f5u2cf"
REGION = "europe-west1"
vertexai.init(project=PROJECT_ID, location=REGION)

pd.set_option('display.max_rows', None)   # Nessun limite per le righe
pd.set_option('display.max_columns', None) # Nessun limite per le colonne
pd.set_option('display.max_colwidth', None) # Nessun limite per la larghezza delle colonne
pd.set_option('display.expand_frame_repr', False)  # Evita che il DataFrame vada su più righe


# generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002")
# response = generative_multimodal_model.generate_content(["Ciao"])
# print(response.text)

def convert_xlsx_to_csv(input_directory, output_directory, sheet):

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".xlsx"):
            xlsx_file = os.path.join(input_directory, filename)
            df = pd.read_excel(xlsx_file, sheet_name=sheet)
            csv_file = os.path.join(output_directory, filename.replace(".xlsx", ".csv"))
            df.to_csv(csv_file, index=False)
            print(f"Converted {xlsx_file} to {csv_file}")

# convert_xlsx_to_csv(input_directory=r"C:\Users\LF84ID\PycharmProjects\Labelling\data\input_data",
#                     output_directory=r"C:\Users\LF84ID\PycharmProjects\Labelling\data\output_data",
#                     sheet="Labeling")

questions = ["Could the bot response be interpreted as advice?",
             "Did the bot provide input on any products that are off-limits?",
             "Inappropriate, rude, racist or provocative language?",
             "Any incorrect and harmful information? ",
             "Any incorrect and UNharmful information?"]

monitoring_data = pd.read_csv(r"C:\Users\LF84ID\PycharmProjects\Labelling\data\output_data\Monitoring file_25092024.csv", header=None)
monitoring_data_mod = monitoring_data.iloc[1:].reset_index(drop=True)

query = list(monitoring_data[4])[2:]
final_answer = list(monitoring_data[7])[2:]
reason = list(monitoring_data[25])[2:]
comment = list(monitoring_data[26])[2:]
url = list(monitoring_data[15])[2:]

data = {
    'query': list(monitoring_data[4])[2:],
    'final_answer': list(monitoring_data[7])[2:],
    'reason': list(monitoring_data[25])[2:],
    'comment': list(monitoring_data[26])[2:],
    'url': list(monitoring_data[15])[2:]
}

df_cleaned = pd.DataFrame(data)
# print(df_cleaned[0:2])

prompt = f"Ciao, riesci a leggere questo dataframe {df_cleaned[0:2]} e a spiegarmi come è fatto?"

prompt = "you are a domain expert of banking area and is ask to you to "

generative_multimodal_model = GenerativeModel("gemini-1.5-pro-002")
response = generative_multimodal_model.generate_content(prompt)
print(response.text)



