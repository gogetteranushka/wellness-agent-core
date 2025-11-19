import os
from dotenv import load_dotenv

load_dotenv()

# Paths
KNOWLEDGE_BASE_PATH = "rag_chatbot/knowledge_base"
VECTOR_STORE_PATH = "rag_chatbot/vectorstore/chromadb"

# Embedding Model
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM Configuration
LLM_PROVIDER = "openai"  # or "gemini"
LLM_MODEL = "gpt-3.5-turbo"  # or "gemini-pro"
LLM_API_KEY = os.getenv("OPENAI_API_KEY")  # or GEMINI_API_KEY

# Retrieval Settings
TOP_K_DOCUMENTS = 3
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
