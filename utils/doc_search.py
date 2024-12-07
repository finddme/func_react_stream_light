
from typing import List, Dict, Tuple
import numpy as np
from openai import OpenAI
import heapq
from model.models import cohere_engine
co= cohere_engine()

class DocumentSearch:
    _instance = None
    _initialized = False 

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, openai_api_key: str = None):
        if DocumentSearch._initialized:
            return
            
        if openai_api_key is None:
            raise ValueError("API key is required for first initialization")
            
        self.documents = []
        self.vectors = []
        self.embedding_client = OpenAI(api_key=openai_api_key)
        DocumentSearch._initialized = True
        
    def get_embedding(self, text: str) -> List[float]:
        response = self.embedding_client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
        
    def add_documents(self, documents: List[Dict]):
        for doc in documents:
            vector = self.get_embedding(doc['content'])
            
            self.vectors.append(vector)
            self.documents.append(doc)
            
    def cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm == 0 or v2_norm == 0:
            return 0.0
            
        return np.dot(v1, v2) / (v1_norm * v2_norm)
        
    def search(self, query: str, k: int = 5) -> List[Tuple[Dict, float]]:
        if not self.vectors:
            return []
            
        query_vector = self.get_embedding(query)
        
        heap = []
        
        for idx, doc_vector in enumerate(self.vectors):
            similarity = self.cosine_similarity(query_vector, doc_vector)
            
            if len(heap) < k:
                heapq.heappush(heap, (similarity, idx))
            elif similarity > heap[0][0]:
                heapq.heapreplace(heap, (similarity, idx))
                
        results = []
        while heap:
            similarity, idx = heapq.heappop(heap)
            results.append((self.documents[idx], similarity))

        final_res = self.rerank(query, results)
            
        return final_res
    
    def rerank(self,query,documents_co):
        global co
        print("--- RERANK ---")

        documents=[d[0]["content"] for d in documents_co]
        
        rerank_res = co.rerank(
            model="rerank-multilingual-v3.0",
            query=query,
            documents=documents, 
            top_n=4, 
        )
        
        doc_txt = ""
        
        for idx,result in enumerate(rerank_res.results):
            doc_txt += f"doc {idx}. {documents[result.index]} \n"

        
        return doc_txt