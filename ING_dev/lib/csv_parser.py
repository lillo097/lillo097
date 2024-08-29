"lo script funziona, va soltanto reingegnerizzato in funzioni."

import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

input_directory = r'C:\Users\lbasile\PycharmProjects\ING_dev\data'
output_directory = r'C:\Users\lbasile\PycharmProjects\ING_dev\csv_data'

# file_path_ops = r"C:\Users\lbasile\PycharmProjects\ING_dev\csv_data\Italy - Chat Bot Report 2024-07-27T06_32_51.072Z.csv"
file_path_intent = r"C:\Users\lbasile\PycharmProjects\ING_dev\NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv"
local_model_path = "./paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(local_model_path)

def convert_xlsx_to_csv(input_directory, output_directory):

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith(".xlsx"):
            xlsx_file = os.path.join(input_directory, filename)
            df = pd.read_excel(xlsx_file, sheet_name="Details")
            csv_file = os.path.join(output_directory, filename.replace(".xlsx", ".csv"))
            df.to_csv(csv_file, index=False)
            print(f"Converted {xlsx_file} to {csv_file}")

def get_file_paths(directory):

    file_paths = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_paths.append(file_path)

    return file_paths

directory_path = r'/csv_data'
paths = get_file_paths(directory_path)

def convert_to_lowercase(df):
    return df.map(lambda x: x.lower() if isinstance(x, str) else x)

def to_title_case(s):
    if isinstance(s, str):
        return s.title()
    return s

def MiniLM_similarity_score(model, sentences):

    embeddings = model.encode(sentences)
    similarity_matrix = cosine_similarity(embeddings)
    # #print("Similarity Matrix:")
    # #print(np.array2string(similarity_matrix, precision=2, suppress_small=True))
    threshold = 0.7  # Define a threshold for similarity
    is_match_intent = similarity_matrix[0][1] > threshold
    is_match_response = similarity_matrix[0][2] > threshold
    #print(f"Match with Intent: {is_match_intent} (Similarity: {similarity_matrix[0][1]:.2f})")
    #print(f"Match with Possible Response: {is_match_response} (Similarity: {similarity_matrix[0][2]:.2f})")
    return f"{similarity_matrix[0][1]:.2f}", f"{similarity_matrix[0][2]:.2f}"


def brutal_run(data_ops, data_intent, path):

    data_ops = convert_to_lowercase(data_ops)
    data_intent = convert_to_lowercase(data_intent)
    filtered_data = data_ops[data_ops["Answer"].isin(["oops! qualcosa non ha funzionato. puoi riprovare oppure cercare le risposte alle tue domande nella sezione aiuto e supporto."])]
    pattern = r'\d{4}-\d{2}-\d{2}'
    match = re.search(pattern, path)
    date = match.group(0)

    session_ids = list(set(filtered_data["Session ID"]))

    ignore_steps = [
        "welcome",
        "no_llm",
        "llm",
        "opening_hours_open_event",
        "workers_available_event",
        "ewt_short_event"
    ]

    columns = ["Step 1", "Step 2", "Step 3", "Step 4"]
    all_steps = []
    for column in columns:
        current_set = set(data_intent[column].tolist())
        for elem in current_set:
            if elem not in all_steps:
                all_steps.append(elem)


    no_llm_session_ids = []
    llm_session_ids = []
    with open(rf"C:\Users\lbasile\PycharmProjects\ING_dev\output\ops_{date}.txt", "a", encoding="utf-8") as file:
        i = 1
        for session_id in session_ids:
            filtered_data_sessionIds = data_ops[data_ops["Session ID"] == session_id]
            conv = filtered_data_sessionIds["Query"].tolist()

            found_llm = False

            for tok in conv:
                if tok == "llm":
                    llm_session_ids.append(session_id)
                    found_llm = True
                    break

            if found_llm:
                continue

            filtered_steps = [step for step in conv if step not in ignore_steps]
            result = f"{i}. " + " --> ".join(filtered_steps) + "\n"
            i += 1
            file.write(result)
            no_llm_session_ids.append(session_id)

    print(llm_session_ids)
    print(len(llm_session_ids))
    print(no_llm_session_ids)
    print(len(no_llm_session_ids))

    with open(rf"C:\Users\lbasile\PycharmProjects\ING_dev\output\ops_{date}.txt", "a") as file:
        file.write("\n")
        for session_id in no_llm_session_ids:
            file.write(session_id)
            file.write("\n")

    check_point = []
    for session_id in no_llm_session_ids:
        filtered_data_sessionIds = data_ops[data_ops["Session ID"] == session_id]
        conv = filtered_data_sessionIds["Query"].tolist()
        filtered_steps = [step for step in conv if step not in ignore_steps]
        conv_path = f"{i}. " + " --> ".join(filtered_steps) + "\n"


        current_df = data_intent.copy()
        old_step = ""
        for i, column in enumerate(columns):
            if i >= len(filtered_steps):
                #print(f"Non ci sono abbastanza passi per la colonna {column}.")
                break

            step = filtered_steps[i]
           # step = to_title_case(filtered_steps[i])
            if "99" in step:
                mod_step = step.replace('99', '24')
                step = mod_step

            if step not in all_steps:
                #print(f"'{step}' is not a step!")
                italian_intent = current_df["description of italian intents contained in the taxonomy (italian version)"].tolist()
                answer = current_df["answers"].tolist()

                #print(len(italian_intent))
                #print(old_step)
                #print(columns[i-1])
                #print(italian_intent[0])
                #print(answer[0])
                check_point.append([step, old_step, columns[i-1], conv_path])
                break

            else:
                #print(current_df["Step 2"])
                if column in current_df.columns:
                    df_filtered = current_df[current_df[column] == step]
                    current_df = df_filtered
                else:
                    #print(f"Colonna '{column}' non trovata nel DataFrame.")
                    current_df = pd.DataFrame()
                #print(f"Passo {i + 1}: {step}")
                #print(f"Colonna: {column}")
                #print("DataFrame filtrato:")
                #print(current_df)
                #print('-' * 40)
                old_step = step

    for elem in check_point:
        filtered_df = data_intent[data_intent[elem[2]].isin([elem[1]])]
        italian_intent = filtered_df["description of italian intents contained in the taxonomy (italian version)"].tolist()
        answer = filtered_df["answers"].tolist()

        with open(rf"C:\Users\lbasile\PycharmProjects\ING_dev\output\similarity_check_{date}.txt", "a", encoding="utf-8") as file:
            for i, a in zip(italian_intent, answer):
                #print("-"*1000)
                #print(f"Richiesta utente: {elem[0]}")
                #print(f"Intento italiano: {i}")
                #print(f"Possibile risposta: {a}")
                match_intent, match_answer = MiniLM_similarity_score(model, [elem[0], i, a])
                #print("-"*1000)

                file.write("-" * 1000 + "\n")
                file.write(f"Path conversazione: {elem[3]}\n")
                file.write(f"Richiesta utente: {elem[0]}\n")
                file.write(f"Intento italiano: {i}\n")
                file.write(f"Possibile risposta: {a}\n")
                file.write(f"Similarity intent score: {match_intent}\n")
                file.write(f"Similarity answer score: {match_answer}\n")
                
                if float(match_intent) > 0.7 or float(match_answer) > 0.7: 
                    print(f"Path conversazione: {elem[3]}\n")
                    print(f"Richiesta utente: {elem[0]}\n")
                    print(f"Intento italiano: {i}\n")
                    print(f"Possibile risposta: {a}\n")
                    print(f"Similarity intent score: {match_intent}\n")
                    print(f"Similarity answer score: {match_answer}\n")
                    print("-"*1000)
                #file.write("-" * 1000 + "\n")

#convert_xlsx_to_csv(input_directory, output_directory)
for path in paths:
    data_ops = pd.read_csv(path, sep=",", encoding='latin1')
    data_intent = pd.read_csv(file_path_intent, sep=",", encoding='latin1')
    brutal_run(data_ops, data_intent, path)
