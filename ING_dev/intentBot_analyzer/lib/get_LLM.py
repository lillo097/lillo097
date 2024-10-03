from sentence_transformers import SentenceTransformer
 
# Specifica il nome del modello
model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
 
# Carica e scarica il modello in una directory locale
model = SentenceTransformer(model_name)
 
# Salva il modello scaricato in una directory locale specificata
model.save('./paraphrase-multilingual-MiniLM-L12-v2-local')
print("Modello scaricato e salvato localmente.")