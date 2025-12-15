# chatbot_api.py - OPTIMIZED VERSION

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from profiler import profiler
import time

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
    description="RAG-based nutrition chatbot with web search",
    version="2.0.0"  # Updated version
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

# Performance tracking middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Track total API request time"""
    start = time.perf_counter()
    
    print(f"\n{'🚀 '*35}")
    print(f"API REQUEST: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    total_time = (time.perf_counter() - start) * 1000
    print(f"\n⏱️  [API_TOTAL_REQUEST_TIME] {total_time:.2f}ms")
    print(f"{'='*70}\n")
    
    return response

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
    llm_model="llama-3.1-8b-instant",
    temperature=0.1,
    top_k=3,
    enable_web_search=True
)
print("✓ RAG pipeline initialized")

@app.get("/")
def root():
    """Root endpoint - API health check"""
    return {
        "message": "FitMind AI Chatbot API v2.0 - Optimized",
        "status": "running",
        "version": "2.0.0",
        "features": ["RAG", "Web Search", "Conversation History"]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    OPTIMIZED chat endpoint - simplified routing
    
    The new RAG pipeline handles:
    - Greetings naturally (no intent classification needed)
    - Demographic filtering automatically
    - Web fallback when uncertain
    
    This endpoint just routes based on user's web search preference
    """
    try:
        profiler.reset()
        api_start = time.perf_counter()
        
        print("\n" + "="*70)
        print(f"[CHAT] Question: {request.question[:50]}...")
        print(f"[CHAT] Web mode: {request.use_web_search}")
        print(f"[CHAT] History: {len(request.conversation_history)} turns")
        print("="*70 + "\n")
        
        # ===== STAGE 1: Request Validation =====
        with profiler.timer("api_1_validation"):
            if not request.question.strip():
                raise HTTPException(400, "Empty question")
            
            history = request.conversation_history or []
        
        # ===== STAGE 2: RAG Pipeline Call =====
        # SIMPLIFIED: Only 3 routing options instead of complex logic
        with profiler.timer("api_2_rag_pipeline"):
            if request.use_web_search is True:
                # User explicitly wants web search
                print("[ROUTING] 🌐 Force Web Search")
                result = rag_pipeline.query_with_web_fallback(
                    question=request.question,
                    force_web=True,
                    conversation_history=history
                )
            
            elif request.use_web_search is False:
                # User explicitly wants local only (no web fallback)
                print("[ROUTING] 📚 Local RAG Only")
                result = rag_pipeline.query(
                    question=request.question,
                    conversation_history=history
                )
            
            else:
                # Auto mode: Try local, fallback to web if uncertain
                print("[ROUTING] 🤖 Auto (Smart Fallback)")
                result = rag_pipeline.query_with_web_fallback(
                    question=request.question,
                    force_web=False,
                    conversation_history=history
                )
        
        print(f"[RESULT] Source type: {result.get('source_type', 'unknown')}")
        
        # ===== STAGE 3: Format Sources =====
        with profiler.timer("api_3_format_sources"):
            sources = None
            
            if request.show_sources:
                source_docs = result.get('source_documents', [])
                
                if result.get('source_type') == 'web':
                    # Web search results
                    sources = [
                        SourceDocument(
                            source=doc.get('url', 'Web Source'),
                            category='web_search',
                            content=doc.get('content', '')[:300]
                        )
                        for doc in source_docs
                    ]
                    print(f"[SOURCES] {len(sources)} web sources")
                
                elif source_docs:
                    # Local RAG documents
                    sources = [
                        SourceDocument(
                            source=doc.metadata.get('source', 'Unknown'),
                            category=doc.metadata.get('category', 'nutrition'),
                            content=doc.page_content[:300]
                        )
                        for doc in source_docs
                    ]
                    print(f"[SOURCES] {len(sources)} local sources")
        
        # ===== STAGE 4: Build Response =====
        with profiler.timer("api_4_build_response"):
            response = ChatResponse(
                question=result['question'],
                answer=result['answer'],
                sources=sources
            )
        
        # Print summary
        api_total = (time.perf_counter() - api_start) * 1000
        print(f"\n⏱️  [API_ENDPOINT_TOTAL] {api_total:.2f}ms")
        print(f"[RESPONSE] Sent {len(sources) if sources else 0} sources")
        profiler.summary("API ENDPOINT PERFORMANCE")
        
        return response
    
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"\n[ERROR] Exception in chat endpoint:\n{error_trace}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "pipeline": "initialized",
        "web_search": rag_pipeline.enable_web_search,
        "model": "llama-3.1-8b-instant",
        "version": "2.0.0"
    }

# Run server
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 Starting FitMind AI API Server v2.0")
    print("=" * 50)
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("\nPress CTRL+C to stop")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
