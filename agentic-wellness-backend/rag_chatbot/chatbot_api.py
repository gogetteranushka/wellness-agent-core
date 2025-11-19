from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn


print("=" * 50)
print("Starting FitMind AI Chatbot API...")
print("=" * 50)


# Import RAG Pipeline
try:
    print("Importing RAG Pipeline...")
    from rag_pipeline import RAGPipeline
    print("✓ RAG Pipeline imported successfully")
except Exception as e:
    print(f"✗ Failed to import RAG Pipeline: {e}")
    raise


# Initialize FastAPI app
print("Creating FastAPI app...")
app = FastAPI(
    title="FitMind AI Chatbot API",
    description="RAG-based nutrition and health chatbot with web search",
    version="1.0.0"
)
print("✓ FastAPI app created")


# Add CORS middleware
print("Adding CORS middleware...")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("✓ CORS middleware added")


# Pydantic Models
class ChatRequest(BaseModel):
    question: str
    show_sources: bool = True
    conversation_history: List[Dict] = []
    use_web_search: Optional[bool] = None  # None = auto, True = force web, False = local only


class SourceDocument(BaseModel):
    source: str
    category: str
    content: str


class ChatResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[SourceDocument]] = None


# Initialize RAG pipeline
print("Initializing RAG pipeline...")
rag_pipeline = RAGPipeline(
    vectorstore_path="rag_chatbot/vectorstore/chromadb",
    llm_model="llama3.2",
    temperature=0.1,
    top_k=3,
    enable_web_search=True
)
print("✓ RAG pipeline initialized")


@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "message": "FitMind AI Chatbot API with Web Search",
        "status": "running",
        "version": "1.0.0"
    }


# @app.post("/chat", response_model=ChatResponse)
# async def chat(request: ChatRequest):
#     """
#     Process chat query with smart web search fallback
    
#     Args:
#         request: ChatRequest with question, sources flag, history, and web search preference
        
#     Returns:
#         ChatResponse with answer and optional source documents
#     """
#     try:
#         print("\n" + "="*50)
#         print(f"[CHAT REQUEST] Question: {request.question}")
#         print(f"[CHAT REQUEST] Web search mode: {request.use_web_search}")
        
#         # Route based on web search preference
#         if request.use_web_search is True:
#             # Force web search
#             print("[ROUTING] Forcing web search")
#             result = rag_pipeline.query_with_web_fallback(request.question, force_web=True)
            
#         elif request.use_web_search is False:
#             # Local only - no web search
#             print("[ROUTING] Local RAG only")
#             if request.conversation_history:
#                 result = rag_pipeline.query_with_history(
#                     request.question,
#                     request.conversation_history
#                 )
#             else:
#                 result = rag_pipeline.query(request.question)
                
#         else:
#             # Auto mode - smart fallback
#             print("[ROUTING] Auto mode (smart fallback)")
#             if request.conversation_history:
#                 result = rag_pipeline.query_with_history(
#                     request.question,
#                     request.conversation_history
#                 )
#             else:
#                 result = rag_pipeline.query_with_web_fallback(request.question)
        
#         print(f"[RAG PIPELINE] Query successful, source: {result.get('source_type', 'unknown')}")
        
#         # Process sources if requested
#         sources = None
#         if request.show_sources:
#             source_docs = result.get('source_documents', [])
            
#             if result.get('source_type') == 'web':
#                 # Web sources
#                 print(f"[SOURCES] Processing {len(source_docs)} web sources")
#                 sources = [
#                     SourceDocument(
#                         source=doc.get('url', 'Web Source'),
#                         category='web_search',
#                         content=doc.get('content', '')[:300]
#                     )
#                     for doc in source_docs
#                 ]
#             elif source_docs:
#                 # Local RAG sources
#                 print(f"[SOURCES] Processing {len(source_docs)} local sources")
#                 sources = [
#                     SourceDocument(
#                         source=doc.metadata.get('source', 'Unknown'),
#                         category=doc.metadata.get('category', 'Unknown'),
#                         content=doc.page_content[:300]
#                     )
#                     for doc in source_docs
#                 ]
        
#         response = ChatResponse(
#             question=result['question'],
#             answer=result['answer'],
#             sources=sources
#         )
        
#         print(f"[RESPONSE] Returning answer with {len(sources) if sources else 0} sources")
#         print("="*50 + "\n")
        
#         return response
    
#     except Exception as e:
#         import traceback
#         error_trace = traceback.format_exc()
#         print(f"\n[ERROR] Exception occurred:\n{error_trace}\n")
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error processing request: {str(e)}"
#         )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat query with smart web search fallback and conversation history
    """
    try:
        print("\n" + "="*50)
        print(f"[CHAT REQUEST] Question: {request.question}")
        print(f"[CHAT REQUEST] Web search mode: {request.use_web_search}")
        print(f"[CHAT REQUEST] History length: {len(request.conversation_history)}")
        
        # Determine if we have meaningful conversation history
        has_history = (
            request.conversation_history is not None 
            and len(request.conversation_history) > 0
        )
        
        # Route based on web search preference
        if request.use_web_search is True:
            # Force web search
            print("[ROUTING] Forcing web search")
            result = rag_pipeline.query_with_web_fallback(request.question, force_web=True)
            
        elif request.use_web_search is False:
            # Local only
            print("[ROUTING] Local RAG only")
            if has_history:
                print("[ROUTING] Using conversation history")
                result = rag_pipeline.query_with_history(
                    request.question,
                    request.conversation_history
                )
            else:
                print("[ROUTING] No conversation history")
                result = rag_pipeline.query(request.question)
                
        else:
            # Auto mode - smart fallback
            print("[ROUTING] Auto mode (smart fallback)")
            if has_history:
                print("[ROUTING] Using conversation history")
                result = rag_pipeline.query_with_history(
                    request.question,
                    request.conversation_history
                )
            else:
                print("[ROUTING] No conversation history, using standard query")
                result = rag_pipeline.query_with_web_fallback(request.question)
        
        print(f"[RAG PIPELINE] Query successful, source: {result.get('source_type', 'unknown')}")
        
        # Process sources if requested
        sources = None
        if request.show_sources:
            source_docs = result.get('source_documents', [])
            
            if result.get('source_type') == 'web':
                # Web sources
                print(f"[SOURCES] Processing {len(source_docs)} web sources")
                sources = [
                    SourceDocument(
                        source=doc.get('url', 'Web Source'),
                        category='web_search',
                        content=doc.get('content', '')[:300]
                    )
                    for doc in source_docs
                ]
            elif source_docs:
                # Local RAG sources
                print(f"[SOURCES] Processing {len(source_docs)} local sources")
                sources = [
                    SourceDocument(
                        source=doc.metadata.get('source', 'Unknown'),
                        category=doc.metadata.get('category', 'Unknown'),
                        content=doc.page_content[:300]
                    )
                    for doc in source_docs
                ]
        
        response = ChatResponse(
            question=result['question'],
            answer=result['answer'],
            sources=sources
        )
        
        print(f"[RESPONSE] Returning answer with {len(sources) if sources else 0} sources")
        print("="*50 + "\n")
        
        return response
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n[ERROR] Exception occurred:\n{error_trace}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )



@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "rag_pipeline": "initialized",
        "web_search": rag_pipeline.enable_web_search
    }


# Run server
if __name__ == "__main__":
    print("=" * 50)
    print("Starting FitMind AI API Server...")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("Press CTRL+C to stop")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
