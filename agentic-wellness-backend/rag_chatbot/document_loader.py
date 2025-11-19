import os
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
class DocumentLoader:
    """Loads and chunks text documents from knowledge base"""
    
    def __init__(self, knowledge_base_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize document loader
        
        Args:
            knowledge_base_path: Path to knowledge base directory
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks for context continuity
        """
        self.knowledge_base_path = knowledge_base_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_documents(self) -> List[Document]:
        """
        Load all txt files from knowledge base and return as Document objects
        
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(self.knowledge_base_path):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Create metadata
                    relative_path = os.path.relpath(file_path, self.knowledge_base_path)
                    category = os.path.dirname(relative_path)
                    
                    metadata = {
                        'source': file,
                        'category': category,
                        'file_path': file_path
                    }
                    
                    # Create Document object
                    doc = Document(page_content=content, metadata=metadata)
                    documents.append(doc)
        
        print(f"Loaded {len(documents)} documents from knowledge base")
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Args:
            documents: List of Document objects
            
        Returns:
            List of chunked Document objects
        """
        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"Split into {len(chunked_docs)} chunks")
        return chunked_docs
    
    def load_and_chunk(self) -> List[Document]:
        """
        Load all documents and chunk them in one step
        
        Returns:
            List of chunked Document objects ready for embedding
        """
        documents = self.load_documents()
        chunked_docs = self.chunk_documents(documents)
        return chunked_docs


# Test function
if __name__ == "__main__":
    # Test the loader
    loader = DocumentLoader(
        knowledge_base_path="rag_chatbot/knowledge_base",
        chunk_size=500,
        chunk_overlap=50
    )
    
    chunks = loader.load_and_chunk()
    
    # Print sample
    print("\n=== Sample Chunk ===")
    print(f"Content: {chunks[0].page_content[:200]}...")
    print(f"Metadata: {chunks[0].metadata}")
