from csv_parser import *
import argparse
import os
import re
import pandas as pd

def main(move_files, convert_switch, filter_flag, key_words, write_DB):
    if move_files:
        file_mover(input_directory=input_directory, output_directory=bkp_directory, clear_directory=output_directory, file_name=None)

    if convert_switch:
        convert_xlsx_to_csv(input_directory, output_directory)

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y-%m-%d")
        paths = get_file_paths(output_directory)
        cake_graph_data = {}
        log_file_path = os.path.join(output_final, f'{formatted_date}_log.txt')
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            for path in paths:
                pattern = r"Chat Bot Report (\d{4}-\d{2}-\d{2})"
                match = re.search(pattern, path)
                if match:
                    report_date = match.group(1)
                    #pbar.set_description(f"Getting access to: Chatbot_report_{report_date}")
                    print(f"\nExecuting: Chatbot_report_{report_date}...")

                data_ops = pd.read_csv(path, sep=",", encoding='latin1')
                data_intent = pd.read_csv(file_path_intent, sep=",", encoding='latin1')

                n_cases, steps, requests = brutal_run(data_ops, data_intent, path, cake_graph_data, filter_flag=filter_flag, key_words=key_words)
                log_file.write(f"{n_cases} 'Ops' cases for Chatbot_report_{report_date}")
                log_file.close()
                if write_DB:
                    gestisci_database(steps, requests, nome_file='queries_DB.json')

            file_mover(output_final, os.path.join(output_final, f"run_{formatted_date}"), clear_directory=None, file_name=f'{formatted_date}_log.txt')
            plot_pie_chart(cake_graph_data)
            delete_empty_content_files_in_subfolder(output_final)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script per spostare file, convertire e generare grafici")

    parser.add_argument('--move_files', type=str, default='False', help='Flag per spostare i file (default: False)')
    parser.add_argument('--convert_switch', type=str, default='False', help='Flag per eseguire la conversione dei file da .xlsx a .csv (default: False)')
    parser.add_argument('--filter_flag', type=str, default='False', help='Flag per abilitare la run filtrata (vedi --key_words) (default: False)')
    parser.add_argument('--key_words', nargs='+', help='Lista di parole chiave per eseguire una run in cui si vogliono osservare i risultati di uno specifico step (es. "mav, rav, f24") (opzionale)', default=None)
    parser.add_argument('--write_DB', type=str, default='False', help='Flag per scrivere su DB delle domande che gli utenti fanno. Se sei sicuro che la run odierna funzioni allora flag su True altrimenti False (default: False)')

    args = parser.parse_args()

    main(
        move_files=args.move_files.lower() == 'true',         # Se non passato, sarà False
        convert_switch=args.convert_switch.lower() == 'true', # Se non passato, sarà False
        filter_flag=args.filter_flag.lower() == 'true',       # Se non passato, sarà False
        key_words=args.key_words if args.key_words != ['None'] else None,  # Converte 'None' a None
        write_DB=args.write_DB.lower() == 'true'
    )

#TO DO: in brutal_run, i parametri key_words e filter_flag possono essere riunificati ad uno unico: se gli passi "if keywrods:" automaticamente dovresti aver rispettato anche la condizione di filtro.