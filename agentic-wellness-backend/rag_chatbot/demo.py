from rag_pipeline import RAGPipeline

rag = RAGPipeline(vectorstore_path="rag_chatbot/vectorstore/chromadb")
docs = rag.vectorstore.similarity_search("diabetes", k=5)
print(f"Found {len(docs)} documents")
for doc in docs:
    print(f"- {doc.metadata.get('source')}: {doc.page_content[:100]}")