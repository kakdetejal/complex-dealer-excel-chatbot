from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")

def get_embeddings(texts):
    return model.encode(texts)

def embed_query(query):
    return model.encode(query)