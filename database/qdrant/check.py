from database.qdrant.vectorStore import create_vector_store,client


info = client.get_collection('807c044f-5d95-44b1-8462-0bee0abd51e9')
print("POINT COUNT:", info.points_count)
