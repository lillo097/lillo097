import pandas as pd
import matplotlib.pyplot as plt

filtered_steps = [['conto corrente', 'operazioni e pagamenti', 'bonifici', 'ciao'],['conto e deposito arancio', 'deposito arancio', 'deposito arancio', 'avvia la chat con un agente', 'avvia la chat con un agente'], ['conto corrente', 'apertura e attivazione', 'conto in attivazione', 'non la carta', 'identificazione con webcam', 'mi poi chemarmi', 'avvia la chat con un agente'], ['carte', 'carta di debito', 'se sospendo la carta di debito , un pagoflex puã² ritirare comunque?', 'pagoflex', 'pagamenti e prelievi', 'avvia la chat con un agente'], ['conto corrente', 'operazioni e pagamenti', 'domiciliazioni e bollettini', 'come mai gli addebiti diretti non funzionano', 'bollettini: come fare', 'non riuscite a collegare mio conto con disposizione di pagamento', 'no', 'si'], ['conto e deposito arancio', 'conto arancio', 'bonifico internazionale', 'operazioni', 'ma cone', 'apertura e attivazione', 'avvia la chat con un agente'], ['carte', 'carta di debito', 'ð\x9f\x98\xadð\x9f\x98\xadð\x9f\x98\xad', 'pagamenti e prelievi', 'contestazione', 'no', 'no', 'si', 'second_topic', 'carte', 'carta di debito', "quanto costa la commissione per prelievi all'estero?", 'opzioni e costi', 'commissione prelievo portogallo', 'pagamenti e prelievi']]

def cake_data(filtered_steps):

    data = pd.read_csv(r'C:\Users\LF84ID\PycharmProjects\lillo097\ING_dev\NLU_mapping_intents_answers_v2 - Copy(Mapping intents-answers).csv', sep=",", encoding='latin1')

    step_1 = list(set(data["Step 1"].dropna()))
    step_1_lower = [elem.lower() for elem in step_1]

    step_2 = list(set(data["Step 2"].dropna()))
    step_2_lower = [elem.lower() for elem in step_2]

    step_3 = list(set(data["Step 3"].dropna()))
    step_3_lower = [elem.lower() for elem in step_3]

    step_4 = list(set(data["Step 4"].dropna()))
    step_4_lower = [elem.lower() for elem in step_4]

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

    cake_graph_data = {}
    if current_last not in cake_graph_data:
        cake_graph_data[current_last] = {"count": 1, "step": step}
    else:
        cake_graph_data[current_last]["count"] += 1
        cake_graph_data[current_last]["step"] = step

    return cake_graph_data


cake_data(filtered_steps[0])
