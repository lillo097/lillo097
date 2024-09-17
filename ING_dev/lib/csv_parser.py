import matplotlib.pyplot as plt
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
from datetime import datetime

input_directory = r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\data'
output_directory = r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\csv_data'

# file_path_ops = r"C:\Users\lbasile\PycharmProjects\ING_dev\csv_data\Italy - Chat Bot Report 2024-07-27T06_32_51.072Z.csv"
file_path_intent = r"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv"
local_model_path = r"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\lib\paraphrase-multilingual-MiniLM-L12-v2-local"
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

directory_path = r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\csv_data'
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

def cake_data(filtered_steps, cake_graph_data):

    data = pd.read_csv(r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv', sep=",", encoding='latin1')

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
        explode=explode,  # Esplosione della fetta più grande
        colors=colors,     # Colori personalizzati
        shadow=True,       # Aggiunta dell'ombra
        wedgeprops={'edgecolor': 'black'},  # Bordo nero attorno alle sezioni
        textprops={'fontsize': 12}  # Imposta la dimensione del testo
    )

    # Migliora la leggibilità delle percentuali all'interno delle sezioni
    for autotext in autotexts:
        autotext.set_color('black')  # Colore bianco per contrasto
        autotext.set_fontsize(14)    # Aumenta la dimensione del testo

    # Migliora il layout delle etichette
    for text in texts:
        text.set_fontsize(12)  # Imposta la dimensione del testo delle etichette

    plt.axis('equal')  # Assicura che il grafico sia un cerchio perfetto
    plt.title('Distribuzione degli Steps', fontsize=16)
    plt.tight_layout()  # Assicura che tutto rientri nella figura

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y-%m-%d")
    output_dir = r"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output"
    run_folder = os.path.join(output_dir, f"run_{formatted_date}")

    plt.savefig(os.path.join(run_folder, "pie_chart.png"))
    plt.show()

def brutal_run(data_ops, data_intent, path, cake_graph_data):

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
    formatted_date = current_date.strftime("%Y-%m-%d")

# Definisci il percorso assoluto della cartella di output

    output_dir = r"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output"
    run_folder = os.path.join(output_dir, f"run_{formatted_date}")
    # Crea la directory 'output\run_{formatted_date}' se non esiste
    if not os.path.exists(run_folder):
        os.makedirs(run_folder)
        print(f"Cartella '{run_folder}' creata con successo!")
    else:
        print(f"Cartella '{run_folder}' esiste già.")

    # Definisci i percorsi per i file che vuoi creare o aprire
    file_path = os.path.join(run_folder, f"ops_{formatted_date}.txt")

    no_llm_session_ids = []
    llm_session_ids = []

    with open(rf"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output\run_{formatted_date}/ops_{date}.txt", "a", encoding="utf-8") as file:
        i = 1
        for session_id in session_ids:
            filtered_data_sessionIds = data_ops[data_ops["Session ID"] == session_id]
            conv = filtered_data_sessionIds["Query"].tolist()
            print(conv)

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

            print(filtered_steps)

            print(filtered_steps)

            cake_data(filtered_steps, cake_graph_data)

            print("°"*1000)
            result = f"{i}. " + " --> ".join(filtered_steps) + "\n"
            i += 1
            file.write(result)
            no_llm_session_ids.append(session_id)

    # print(llm_session_ids)
    # print(len(llm_session_ids))
    # print(no_llm_session_ids)
    # print(len(no_llm_session_ids))

    with open(rf"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output\run_{formatted_date}/ops_{date}.txt", "a") as file:
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

        with open(rf"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output\run_{formatted_date}/similarity_check_{date}.txt", "a", encoding="utf-8") as file:
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
                
                if float(match_intent) > 0.55 or float(match_answer) > 0.55:
                    with open(rf"C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\output\run_{formatted_date}/best_similarity_scores.txt", "a", encoding="utf-8") as file1:
                        file1.write("\n")
                        file1.write(f"Data: {date}\n")
                        file1.write("\n")
                        file1.write(f"Path conversazione: {elem[3]}\n")
                        file1.write(f"Richiesta utente: {elem[0]}\n")
                        file1.write(f"\n")
                        file1.write(f"Intento italiano: {i}\n")
                        file1.write(f"\n")
                        file1.write(f"Possibile risposta: {a}\n")
                        file1.write(f"Similarity intent score: {match_intent}\n")
                        file1.write(f"Similarity answer score: {match_answer}\n")
                        file1.write("\n")
                        file1.write(f"{'°'*1000}\n")

                    # print(f"Path conversazione: {elem[3]}\n")
                    # print(f"Richiesta utente: {elem[0]}\n")
                    # print(f"Intento italiano: {i}\n")
                    # print(f"Possibile risposta: {a}\n")
                    # print(f"Similarity intent score: {match_intent}\n")
                    # print(f"Similarity answer score: {match_answer}\n")
                    # print("-"*1000)
                #file.write("-" * 1000 + "\n")




#convert_xlsx_to_csv(input_directory, output_directory)

cake_graph_data = {}
for path in paths:
    data_ops = pd.read_csv(path, sep=",", encoding='latin1')
    data_intent = pd.read_csv(file_path_intent, sep=",", encoding='latin1')

    brutal_run(data_ops, data_intent, path, cake_graph_data)

plot_pie_chart(cake_graph_data)


