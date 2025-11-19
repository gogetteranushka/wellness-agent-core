from typing import List
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

class VectorStoreManager:
    """Manages ChromaDB vector store for document embeddings"""
    
    def __init__(self, persist_directory: str, embedding_model_name: str):
        """
        Initialize vector store manager
        
        Args:
            persist_directory: Directory to persist ChromaDB
            embedding_model_name: Name of embedding model
        """
        self.persist_directory = persist_directory
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
    
    def create_vectorstore(self, documents: List[Document]) -> Chroma:
        """
        Create a new vector store from documents
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            ChromaDB vector store
        """
        print(f"Creating vector store with {len(documents)} documents...")
        
        self.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        
        print(f"Vector store created and persisted to {self.persist_directory}")
        return self.vectorstore
    
    def load_vectorstore(self) -> Chroma:
        """
        Load existing vector store from disk
        
        Returns:
            ChromaDB vector store
        """
        print(f"Loading vector store from {self.persist_directory}...")
        
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        
        print("Vector store loaded successfully")
        return self.vectorstore
    
    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Query text
            k: Number of top results to return
            
        Returns:
            List of most similar documents
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore() or load_vectorstore() first.")
        
        results = self.vectorstore.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 3) -> List[tuple]:
        """
        Search for similar documents with similarity scores
        
        Args:
            query: Query text
            k: Number of top results to return
            
        Returns:
            List of tuples (document, score)
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vectorstore() or load_vectorstore() first.")
        
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        return results


# Test function
if __name__ == "__main__":
    from document_loader import DocumentLoader
    
    # Load and chunk documents
    print("=== Loading Documents ===")
    loader = DocumentLoader(
        knowledge_base_path="rag_chatbot/knowledge_base",
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = loader.load_and_chunk()
    
    # Create vector store
    print("\n=== Creating Vector Store ===")
    vector_manager = VectorStoreManager(
        persist_directory="rag_chatbot/vectorstore/chromadb",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vector_manager.create_vectorstore(chunks)
    
    # Test similarity search
    print("\n=== Testing Similarity Search ===")
    test_query = "What should diabetic patients eat?"
    results = vector_manager.similarity_search_with_score(test_query, k=3)
    
    print(f"\nQuery: {test_query}\n")
    for i, (doc, score) in enumerate(results, 1):
        print(f"Result {i} (Score: {score:.4f}):")
        print(f"Source: {doc.metadata['source']}")
        print(f"Content: {doc.page_content[:200]}...\n")
