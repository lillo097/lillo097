from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load the model from the local directory
local_model_path = "./paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(local_model_path)

# Define the sentences
sentences = [
    "al mio gatto piace il pesce crudo e ama giocare",
    "la mia tigre adora il tonno e ama giocare",
    "ho visto un leopardo mangiare un delfino"]

# Encode sentences to get embeddings
embeddings = model.encode(sentences)

# Compute cosine similarity between embeddings
similarity_matrix = cosine_similarity(embeddings)

# Print the similarity matrix
print("Similarity Matrix:")
print(np.array2string(similarity_matrix, precision=2, suppress_small=True))

# Check if the first sentence matches with the intent and possible response
threshold = 0.7  # Define a threshold for similarity
is_match_intent = similarity_matrix[0][1] > threshold
is_match_response = similarity_matrix[0][2] > threshold

print(f"Match with Intent: {is_match_intent} (Similarity: {similarity_matrix[0][1]:.2f})")
print(f"Match with Possible Response: {is_match_response} (Similarity: {similarity_matrix[0][2]:.2f})")
