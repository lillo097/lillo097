import json
import os

def gestisci_database(chiavi, frasi, nome_file='queries_DB.json'):
    def aggiorna_database(chiavi, frasi, database):
        for chiave, frase in zip(chiavi, frasi):
            if chiave:
                if chiave in database:
                    database[chiave].append(frase)
                else:
                    database[chiave] = [frase]

    if os.path.exists(nome_file):
        with open(nome_file, 'r') as f:
            database = json.load(f)
    else:
        database = {}

    aggiorna_database(chiavi, frasi, database)

    with open(nome_file, 'w') as f:
        json.dump(database, f, indent=4)


# Esempio di utilizzo
chiavi = ['codici di accesso', 'assegni', 'bonifici', 'prestito in corso', 'conto arancio', 'conto arancio', '', '', '', '', 'bonifici', 'codici di accesso', '', 'carta di credito', 'carta di debito', 'bonifici']
frasi = ["non riesco ad attivare l'app ing", 'vorrei parlare con un operatore', 'vorrei bloccare una transazione', 'ho richiesto un prestito. quando arriverã\xa0 la risposta e come?', 'come sono calcolati gli interessi di postcodeeuro attesi a fine anno sul mio conto?', 'come aprire conto arancio con digit% interessi', 'forse non mi sono spiegata bene', 'buongiorno sig. lorenzo', 'ho la carta di credito che non funziona piã¹ in modalitã\xa0 wireless ã¨ possibile avere un duplicato ?', 'rateizzare importo carta di credito', 'ho fatto un bonifico ieri ma il destinatario non ha ancora ricevuto', 'come fare a contattarvi telefonicamente?', 'buonasera , volevo sapere a quanto ammonta imposta di bollo sul conto depositi conto arancio .', 'non funziona piã¹ il contactless nella mia carta di credito', 'carta bloccata per pin errato', 'buongiorno ã¨ stato fatto un pagamento su lightspeed che non ã¨ stato fatto da me']

# Prima esecuzione: crea e aggiorna il database
gestisci_database(chiavi, frasi)

# Nuove liste per un aggiornamento successivo
chiavi_1 = ['codici di accesso', 'assegni', 'mammeta']
frasi_1 = ["mario", "rossi", "bucchin"]

# Seconda esecuzione: aggiorna il database esistente
gestisci_database(chiavi_1, frasi_1)

