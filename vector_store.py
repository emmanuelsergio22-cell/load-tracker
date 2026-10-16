import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="day_logs")

def store_day(log_id, user_id, date, text):
    collection.add(
        ids=[str(log_id)],
        documents=[text],
        metadatas=[{"user_id": user_id, "date": date}],
    )

def find_similar_days(user_id, text, n_results=3):
    results = collection.query(
        query_texts=[text],
        n_results=n_results,
        where={"user_id": user_id},
    )
    return results