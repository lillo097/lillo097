import subprocess
import time

def run_commands():
    try:
        # Comando 1: ngrok http 6000
        ngrok_process = subprocess.Popen(['ngrok', 'http', '6000'])
        time.sleep(2)  # Attendiamo qualche secondo per assicurarci che ngrok abbia avuto il tempo di avviarsi

        # Comando 3: python app.py nella directory /Users/liviobasile/Downloads/Diet_builder/library
        app_process = subprocess.Popen(['python', 'app.py'], cwd='/Users/liviobasile/Documents/Machine Learning/lillo097/Diet_builder/library')
        app_process.wait()  # Attendiamo il completamento di app.py prima di uscire

        # Attendiamo il completamento di ngrok e lo terminiamo
        ngrok_process.terminate()
        ngrok_process.wait()

    except KeyboardInterrupt:
        # Gestione interruzione da tastiera (Ctrl+C)
        print("Interruzione manuale, terminazione dei processi...")
        ngrok_process.terminate()
        app_process.terminate()

if __name__ == "__main__":
    run_commands()
