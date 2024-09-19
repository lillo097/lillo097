import matplotlib.pyplot as plt
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from datetime import datetime
from tqdm import tqdm
import time
import sys
import configparser

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

def get_project_path(*subdirs):

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ING_dev_folder = current_dir.replace("\lib", "")
    full_path = os.path.join(ING_dev_folder, *subdirs)

    return full_path

# input_directory = r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\data'
# output_directory = r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\csv_data'
# # file_path_ops = r"C:\Users\lbasile\PycharmProjects\ING_dev\csv_data\Italy - Chat Bot Report 2024-07-27T06_32_51.072Z.csv"
# file_path_intent = r"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv"
#local_model_path = r"C:\Users\lbasile\PycharmProjects\lillo097\ING_dev\paraphrase-multilingual-MiniLM-L12-v2-local"

config_file = get_project_path('lib', 'config.properties')
config = configparser.ConfigParser()
config.read(config_file)
convert_switch = config.get('Parameters', 'convert_switch')
key_words = config.get('Parameters', 'key_words').split(', ')

input_directory = get_project_path('data')
output_directory = get_project_path('csv_data')
output_final = get_project_path('output')
file_path_intent = get_project_path('NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv')
local_model_path = get_project_path('paraphrase-multilingual-MiniLM-L12-v2-local')

model = SentenceTransformer(local_model_path)
paths = get_file_paths(output_directory)

def convert_to_lowercase(df):
    return df.map(lambda x: x.lower() if isinstance(x, str) else x)

def to_title_case(s):
    if isinstance(s, str):
        return s.title()
    return s

def delete_empty_content_files_in_subfolder(output_folder):
    if not os.path.isdir(output_folder):
        (f"La cartella '{output_folder}' non esiste.")
        return

    subfolders = [f.path for f in os.scandir(output_folder) if f.is_dir()]

    if not subfolders:
        print(f"Nessuna sottocartella trovata nella cartella '{output_folder}'.")
        return

    subfolder = subfolders[0]
    for file_name in os.listdir(subfolder):
        file_path = os.path.join(subfolder, file_name)

        if os.path.isfile(file_path):

            if file_name.lower().endswith('.png'):
                #print(f"Ignorando il file PNG: '{file_path}'")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()

                if not content:
                    time.sleep(0.1)
                    os.remove(file_path)
                    #print(f"File '{file_path}' eliminato perché vuoto (o contenente solo spazi).")
                # else:
                #     print(f"File '{file_path}' contiene testo, non eliminato.")
            except PermissionError as e:
                print(f"Errore: Impossibile eliminare '{file_path}' perché è in uso: {e}")
            except Exception as e:
                print(f"Errore: Si è verificato un problema con il file '{file_path}': {e}")

        # elif os.path.isfile(file_path) == "pie_chart.png":
        #     continue

def MiniLM_similarity_score(model, sentences):

    embeddings = model.encode(sentences)
    similarity_matrix = cosine_similarity(embeddings)
    threshold = 0.7  # Define a threshold for similarity
    is_match_intent = similarity_matrix[0][1] > threshold
    is_match_response = similarity_matrix[0][2] > threshold
    #print(f"Match with Intent: {is_match_intent} (Similarity: {similarity_matrix[0][1]:.2f})")
    #print(f"Match with Possible Response: {is_match_response} (Similarity: {similarity_matrix[0][2]:.2f})")
    return f"{similarity_matrix[0][1]:.2f}", f"{similarity_matrix[0][2]:.2f}"

def cake_data(filtered_steps, cake_graph_data):

    data = pd.read_csv(file_path_intent, sep=",", encoding='latin1')

    step_1 = list(set(data["Step 1"].dropna()))
    step_1_lower = [elem.lower() for elem in step_1]

    step_2 = list(set(data["Step 2"].dropna()))
    step_2_lower = [elem.lower() for elem in step_2]

    step_3 = list(set(data["Step 3"].dropna()))
    step_3_lower = [elem.lower() for elem in step_3]

    step_4 = list(set(data["Step 4"].dropna()))
    step_4_lower = [elem.lower() for elem in step_4]

    current_last = ''
    step = ''
    if filtered_steps[0] in step_1_lower:
        step = "step_1"
        current_last = filtered_steps[0]

    if len(filtered_steps) > 1 and filtered_steps[1] in step_2_lower:
        step = "step_2"
        current_last = filtered_steps[1]

    if len(filtered_steps) > 2 and filtered_steps[2] in step_3_lower:
        step = "step_3"
        current_last = filtered_steps[2]

    if len(filtered_steps) > 3 and filtered_steps[3] in step_4_lower:
        step = "step_4"
        current_last = filtered_steps[3]
    # else:
    #     current_last = "None"

    if current_last not in cake_graph_data and current_last != "None":
        cake_graph_data[current_last] = {"count": 1, "step": step}
    else:
        cake_graph_data[current_last]["count"] += 1
        cake_graph_data[current_last]["step"] = step

def plot_pie_chart(cake_graph_data):
    labels = list(cake_graph_data.keys())
    sizes = [value['count'] for value in cake_graph_data.values()]

    # Colori personalizzati
    colors = plt.get_cmap('tab20')(range(len(sizes)))  # Palette di colori

    # Esplosione per enfatizzare la fetta più grande
    explode = [0.1 if size == max(sizes) else 0 for size in sizes]

    plt.figure(figsize=(15, 15))

    # Grafico a torta con effetti visivi migliorati
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        explode=explode,
        colors=colors,
        shadow=True,
        wedgeprops={'edgecolor': 'black'},
        textprops={'fontsize': 12}
    )

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontsize(14)

    for text in texts:
        text.set_fontsize(12)

    plt.axis('equal')
    plt.title('Distribuzione degli Steps', fontsize=16)
    plt.tight_layout()

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")

    run_folder = os.path.join(output_final, f"run_{formatted_date}")

    plt.savefig(os.path.join(run_folder, "pie_chart.png"))
    #plt.show()

def brutal_run(data_ops, data_intent, path, cake_graph_data, filter_flag:bool, key_words:list):

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

    current_date = datetime.now()
    formatted_date = current_date.strftime("%d-%m-%Y")

    run_folder = os.path.join(output_final, f"run_{formatted_date}")

    if not os.path.exists(run_folder):
        os.makedirs(run_folder)
    #     print(f"Cartella '{run_folder}' creata con successo!")
    # else:
    #     print(f"Cartella '{run_folder}' esiste già.")

    no_llm_session_ids = []
    llm_session_ids = []
    no_llm_session_ids_filtered = []
    path = os.path.join(output_final, f"run_{formatted_date}", f"ops_{date}.txt")

    with tqdm(total=len(session_ids), desc="Evaluating ops...", unit='item', disable=True) as pbar:
        with open(path, "a", encoding="utf-8") as file:

            i = 1
            for session_id in session_ids:
                #print('\n')
                filtered_data_sessionIds = data_ops[data_ops["Session ID"] == session_id]
                conv = filtered_data_sessionIds["Query"].tolist()
                # print(conv)

                found_llm = False

                for tok in conv:
                    if tok == "llm":
                        llm_session_ids.append(session_id)
                        found_llm = True
                        break

                if found_llm:
                    continue

                filtered_steps = [step for step in conv if step not in ignore_steps]
                filtered_steps = [step.replace('99', '24') if '99' in step else step for step in filtered_steps]

                cake_data(filtered_steps, cake_graph_data)

                if filter_flag and key_words is not None:
                    check = False
                    for step in filtered_steps:
                        if any(element in step for element in key_words):
                            if session_id not in no_llm_session_ids_filtered:
                                no_llm_session_ids_filtered.append(session_id)
                                check = True

                    if check:
                        result = f"{i}. " + " --> ".join(filtered_steps) + "\n"
                        i += 1
                        file.write(result)

                else:
                    result = f"{i}. " + " --> ".join(filtered_steps) + "\n"
                    i += 1
                    file.write(result)
                    no_llm_session_ids.append(session_id)

                #pbar.update(1)
        # print(llm_session_ids)
        # print(len(llm_session_ids))
        # print(no_llm_session_ids)
        # print(len(no_llm_session_ids))

        if filter_flag == True:
            current_session_ids = no_llm_session_ids_filtered
        else:
            current_session_ids = no_llm_session_ids

        with open(os.path.join(output_final, f"run_{formatted_date}/ops_{date}.txt"), "a") as file:
            file.write("\n")
            for session_id in current_session_ids:
                file.write(session_id)
                file.write("\n")

        check_point = []

        with tqdm(total=len(current_session_ids), desc="Evaluating ops...", unit='item', disable=False, leave=True) as pbar:
            for session_id in current_session_ids:
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
                        #print(f"Colonna: {column}")
                        #print("DataFrame filtrato:")
                        #print(current_df)
                        #print('-' * 40)
                        old_step = step

                pbar.update(1)
                sys.stdout.flush()



    with tqdm(total=len(check_point), desc="Doing similarity...", unit="item") as pbar:
        for elem in check_point:
            filtered_df = data_intent[data_intent[elem[2]].isin([elem[1]])]
            italian_intent = filtered_df["description of italian intents contained in the taxonomy (italian version)"].tolist()
            answer = filtered_df["answers"].tolist()

            # Definisci il percorso del file e aprilo in modalità append
            file_path = os.path.join(output_final, f'run_{formatted_date}/similarity_check_{date}.txt')
            with open(file_path, "a", encoding="utf-8") as file:
                # Scrivi i dettagli di ciascun elemento nel file
                for i, a in zip(italian_intent, answer):
                    match_intent, match_answer = MiniLM_similarity_score(model, [elem[0], i, a])

                    file.write("-" * 1000 + "\n")
                    file.write(f"Path conversazione: {elem[3]}\n")
                    file.write(f"Richiesta utente: {elem[0]}\n")
                    file.write(f"Intento italiano: {i}\n")
                    file.write(f"Possibile risposta: {a}\n")
                    file.write(f"Similarity intent score: {match_intent}\n")
                    file.write(f"Similarity answer score: {match_answer}\n")

                    if float(match_intent) > 0.55 or float(match_answer) > 0.55:
                        best_file_path = os.path.join(output_final, f'run_{formatted_date}/best_similarity_scores.txt')
                        with open(best_file_path, "a", encoding="utf-8") as file1:
                            file1.write("\n")
                            file1.write(f"Data: {date}\n")
                            file1.write("\n")
                            file1.write(f"Path conversazione: {elem[3]}\n")
                            file1.write(f"Richiesta utente: {elem[0]}\n")
                            file1.write("\n")
                            file1.write(f"Intento italiano: {i}\n")
                            file1.write("\n")
                            file1.write(f"Possibile risposta: {a}\n")
                            file1.write(f"Similarity intent score: {match_intent}\n")
                            file1.write(f"Similarity answer score: {match_answer}\n")
                            file1.write("\n")
                            file1.write(f"{'°'*1000}\n")

            # Aggiorna la barra di avanzamento
            pbar.update(1)
            sys.stdout.flush()


                    # print(f"Path conversazione: {elem[3]}\n")
                    # print(f"Richiesta utente: {elem[0]}\n")
                    # print(f"Intento italiano: {i}\n")
                    # print(f"Possibile risposta: {a}\n")
                    # print(f"Similarity intent score: {match_intent}\n")
                    # print(f"Similarity answer score: {match_answer}\n")
                    # print("-"*1000)
                #file.write("-" * 1000 + "\n")

if convert_switch:
    convert_xlsx_to_csv(input_directory, output_directory)
else:
    cake_graph_data = {}
    with tqdm(total=len(paths)) as pbar:
        for path in paths:
            pattern = r"Chat Bot Report (\d{4}-\d{2}-\d{2})"
            match = re.search(pattern, path)
            if match:
                report_date = match.group(1)
            pbar.set_description(f"Getting access to: Chatbot_report_{report_date}")
            data_ops = pd.read_csv(path, sep=",", encoding='latin1')
            data_intent = pd.read_csv(file_path_intent, sep=",", encoding='latin1')

            brutal_run(data_ops, data_intent, path, cake_graph_data, filter_flag=False, key_words=None)
            pbar.update(1)
            sys.stdout.flush()




    plot_pie_chart(cake_graph_data)
    delete_empty_content_files_in_subfolder(output_final)


