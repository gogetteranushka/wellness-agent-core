from typing import List
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from sentence_transformers import SentenceTransformer

class EmbeddingGenerator:
    """Generates embeddings for text chunks using sentence transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        print(f"Loading embedding model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},  
            encode_kwargs={'normalize_embeddings': True}
        )
        print("Embedding model loaded successfully")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.embeddings.embed_documents(texts)
        return embeddings
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a single query
        
        Args:
            query: Query text string
            
        Returns:
            Embedding vector
        """
        embedding = self.embeddings.embed_query(query)
        return embedding


# Test function
if __name__ == "__main__":
    # Test the embedding generator
    generator = EmbeddingGenerator()
    
    # Test with sample text
    sample_texts = [
        "What are the symptoms of diabetes?",
        "How to manage high blood pressure?"
    ]
    
    embeddings = generator.generate_embeddings(sample_texts)
    
    print(f"\n=== Embedding Results ===")
    print(f"Generated embeddings for {len(sample_texts)} texts")
    print(f"Embedding dimension: {len(embeddings[0])}")
    print(f"First embedding (first 10 values): {embeddings[0][:10]}")
