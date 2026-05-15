import chromadb

class LongTermMemory:
    def __init__(self, collection_name: str = "agent_experience"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
    
    def store_experience(self, query: str, action: str, result: str, success: bool):
        """Сохранить опыт: что спросили, что сделали, какой результат"""
        self.collection.add(
            documents=[f"Query: {query}\nAction: {action}\nResult: {result}"],
            metadatas=[{"success": success, "action": action}],
            ids=[f"exp_{len(self.collection.get()['ids'])}"]
        )
    
    def find_similar(self, query: str, n_results: int = 3) -> list:
        """Найти похожий прошлый опыт"""
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0] if results['documents'] else []