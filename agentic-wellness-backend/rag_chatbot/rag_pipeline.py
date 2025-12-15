# rag_pipeline.py - OPTIMIZED VERSION (No Intent Classification)

from typing import List, Dict, Optional
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tavily import TavilyClient
import os
from dotenv import load_dotenv
import time
from profiler import profiler

load_dotenv()

class RAGPipeline:
    def __init__(
        self,
        vectorstore_path: str = "rag_chatbot/vectorstore/chromadb",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "llama-3.1-8b-instant",
        temperature: float = 0.1,
        top_k: int = 3,
        enable_web_search: bool = True,
    ):
        """Initialize RAG pipeline"""
        
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        self.enable_web_search = enable_web_search

        # Initialize embeddings
        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Load vector store
        print("Loading vector store...")
        self.vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=self.embeddings
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": top_k}
        )
        
        # Initialize Groq LLM
        print("Initializing Groq LLM...")
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        self.llm = ChatGroq(
            model=llm_model,
            temperature=temperature,
            api_key=groq_api_key,
            max_tokens=512,
            timeout=10.0
        )
        print(f"✓ Groq LLM initialized with model: {llm_model}")
        
        # Initialize Tavily web search
        if enable_web_search:
            try:
                tavily_api_key = os.getenv("TAVILY_API_KEY")
                if tavily_api_key:
                    self.tavily_client = TavilyClient(api_key=tavily_api_key)
                    print("✓ Web search enabled with Tavily")
                else:
                    print("⚠ TAVILY_API_KEY not found. Web search disabled.")
                    self.enable_web_search = False
            except Exception as e:
                print(f"⚠ Failed to initialize Tavily: {e}")
                self.enable_web_search = False
        
        # Create prompt template
        self.prompt = self._create_prompt_template()
        
        print("RAG pipeline initialized successfully!\n")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Optimized prompt that handles greetings AND nutrition queries"""
        template = """You are FitMind AI, a nutrition assistant specializing in Indian dietary advice.

Chat history:
{chat_history}

Knowledge base context:
{context}


User question: {question}

INTERNAL DECISION PROCESS (don't show this to user):

1. Is this question EXACTLY a greeting word?
   - Greeting words ONLY: "hi", "hello", "hey", "thanks", "thank you", "bye", "goodbye"
   - NOT greetings: "what is...", "who should...", "how to...", "can you..."
   
   If YES (exact greeting): Say "Namaste! I'm FitMind AI, your nutrition assistant. Ask me about diabetes diet, meal plans, or health conditions!"
   
   If NO (not a greeting): Continue to step 2

2. Is this a NEW topic or FOLLOW-UP?
   - NEW: "what is diabetes?" (asking for definition)
   - FOLLOW-UP: "what about lunch?" (continuing previous discussion)
   
   If NEW: Ignore conversation history, answer current question only
   If FOLLOW-UP: Use conversation history for context

3. Check user's demographic constraints and filter documents:
   - If user says "vegetarian": IGNORE any documents with "animal_foods", "meat", "fish", "poultry" in the source name
   - If user says "vegan": IGNORE any documents with "animal_foods", "meat", "fish", "dairy", "egg", "milk" in the source name
   - If user says "male" OR mentions age 18-60 WITHOUT "pregnant"/"lactating": IGNORE any documents with "pregnant", "pregnancy", "lactating" in the source name
   - If user says "child" OR mentions age under 18: IGNORE any documents with "pregnant", "pregnancy", "lactating", "adult" in the source name
   - After filtering, use ONLY the remaining relevant documents to answer

4. Does knowledge base have relevant info (after filtering)?
   - YES: Answer using context (2-3 sentences, focus on nutrition, Indian foods)
   - NO or OUT-OF-SCOPE (exercise/gym/medicine): Say "I don't have specific information about that in my knowledge base."

IMPORTANT:
- NEVER say "Namaste!" unless the question is an EXACT greeting word
- NEVER show your reasoning (no "STEP 1", "analyzing", etc.)
- Answer directly and naturally
- Keep it concise (2-3 sentences)

HARD CONSTRAINTS (must never be violated):
- If the user is vegetarian, NEVER use or cite documents related to animal foods, meat, fish, poultry, eggs, or dairy unless the user explicitly allows them.
- Unless the user explicitly states pregnancy or lactation, assume they are NOT pregnant or lactating and NEVER use pregnancy or lactation-related documents.
- If a document violates the user’s dietary type or life stage, it must be COMPLETELY IGNORED even if present in the context.


Answer:"""
        
        return ChatPromptTemplate.from_template(template)
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    def _get_demographic_filter(self, question: str) -> Optional[dict]:
        """Simple demographic filtering for Chroma"""
        question_lower = question.lower()
        
        # Exclude pregnancy docs for males/children
        if any(word in question_lower for word in ['male', 'man', 'boy', 'men']):
            return {"category": {"$nin": ["pregnant_women", "lactating_women", "pregnancy"]}}
        
        if any(word in question_lower for word in ['child', 'children', 'kid', 'toddler']):
            return {"category": {"$nin": ["pregnant_women", "lactating_women", "adult"]}}
        
        return None  # No filter
    
    def query(self, question: str, conversation_history: List[Dict] | None = None) -> Dict:
        """Query with post-filtering using the same filter logic"""
        if conversation_history is None:
            conversation_history = []
        
        profiler.reset()
        total_start = time.perf_counter()
        
        print(f"\n{'='*70}")
        print(f"🔍 QUERY: {question[:60]}...")
        print(f"{'='*70}\n")
        
        # STAGE 1: Vector retrieval with post-filtering
        with profiler.timer("1_vector_search"):
            # Get filter criteria (what to exclude)
            filter_dict = self._get_demographic_filter(question)
            
            if filter_dict:
                # We know what to exclude, so fetch more candidates
                print(f"[FILTER] Demographic filtering enabled")
                all_docs = self.vectorstore.similarity_search(question, k=15)
                
                # Extract exclusion list from filter_dict
                # filter_dict = {'category': {'$nin': ['pregnant_women', 'lactating_women', 'pregnancy']}}
                excluded_categories = filter_dict.get('category', {}).get('$nin', [])
                
                print(f"[FILTER] Excluding categories: {excluded_categories}")
                
                # Post-filter: Check SOURCE filename for keywords
                # Map category names to filename keywords
                category_to_keywords = {
                    'pregnant_women': ['pregnant', 'pregnancy'],
                    'lactating_women': ['lactating', 'lactation'],
                    'pregnancy': ['pregnant', 'pregnancy'],
                    'adult': ['adult']
                }
                
                # Build list of keywords to exclude based on filter_dict
                exclude_keywords = []
                for cat in excluded_categories:
                    exclude_keywords.extend(category_to_keywords.get(cat, []))
                
                # Remove duplicates
                exclude_keywords = list(set(exclude_keywords))
                print(f"[FILTER] Excluding source files containing: {exclude_keywords}")
                
                # Filter documents by checking SOURCE filename
                source_docs = []
                excluded_count = 0
                
                for doc in all_docs:
                    source_name = doc.metadata.get('source', '').lower()
                    
                    # Check if source contains any excluded keyword
                    should_exclude = any(keyword in source_name for keyword in exclude_keywords)
                    
                    if should_exclude:
                        excluded_count += 1
                        print(f"[FILTER]   ✗ Excluded: {doc.metadata.get('source', 'Unknown')}")
                    else:
                        source_docs.append(doc)
                        if len(source_docs) >= self.top_k:
                            break  # Got enough
                
                print(f"[FILTER] ✓ Kept {len(source_docs)} docs, excluded {excluded_count} docs")
            
            else:
                # No filtering needed
                print(f"[FILTER] No demographic filtering needed")
                source_docs = self.vectorstore.similarity_search(question, k=self.top_k)
        
        print(f"[RETRIEVAL] {len(source_docs)} final documents")
        
        # Show final docs
        for i, doc in enumerate(source_docs, 1):
            print(f"[DOC {i}] {doc.metadata.get('source', 'Unknown')}")
        
        # STAGE 2: Build context
        with profiler.timer("2_context_build"):
            context = self._format_docs(source_docs) if source_docs else "No specific information found."
            history = "\n".join([
                f"User: {t['question'][:100]}\nAssistant: {t['answer'][:150]}" 
                for t in conversation_history[-3:]
            ]) if conversation_history else ""
        
        # STAGE 3: Groq generation
        with profiler.timer("3_groq_generation"):
            try:
                print("[GROQ] Generating answer...")
                prompt_value = self.prompt.format(
                    context=context,
                    question=question,
                    chat_history=history
                )
                answer = self.llm.invoke(prompt_value).content
                print(f"[GROQ] ✓ Generated: {answer[:80]}...")
            except Exception as e:
                print(f"[GROQ ERROR] {e}")
                answer = "I'm experiencing technical difficulties. Please try again."
        
        total_time = (time.perf_counter() - total_start) * 1000
        print(f"\n⏱️  [TOTAL] {total_time:.2f}ms")
        profiler.summary("QUERY PERFORMANCE")
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": source_docs,
            "source_type": "local"
        }

    def web_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """Perform web search using Tavily"""
        if not self.enable_web_search:
            return []
        
        try:
            print(f"[WEB] Searching: {query}")
            
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",
                include_answer=False,
                include_raw_content=False
            )
            
            results = [
                {
                    'title': r.get('title', ''),
                    'url': r.get('url', ''),
                    'content': r.get('content', ''),
                    'score': r.get('score', 0)
                }
                for r in response.get('results', [])
            ]
            
            print(f"[WEB] Found {len(results)} results")
            return results
        
        except Exception as e:
            print(f"[WEB ERROR] {e}")
            return []
    
    # def query_with_web_fallback(
    #     self,
    #     question: str,
    #     force_web: bool = False,
    #     conversation_history: List[Dict] | None = None,
    # ) -> Dict:
    #     """Query with smart web search fallback"""
        
    #     if conversation_history is None:
    #         conversation_history = []
        
    #     profiler.reset()
    #     total_start = time.perf_counter()
        
    #     # Force web search
    #     if force_web:
    #         print("[HYBRID] Force web search")
    #         with profiler.timer("web_search"):
    #             web_results = self.web_search(question)
            
    #         with profiler.timer("web_answer"):
    #             result = self._generate_web_answer(question, web_results)
            
    #         total_time = (time.perf_counter() - total_start) * 1000
    #         print(f"\n⏱️  [TOTAL_WEB] {total_time:.2f}ms")
    #         profiler.summary("WEB SEARCH PERFORMANCE")
    #         return result
        
    #     # Try local RAG first
    #     print("[HYBRID] Trying local RAG...")
    #     with profiler.timer("local_rag"):
    #         local_result = self.query(question, conversation_history=conversation_history)
        
    #     # Check if answer indicates no information
    #     with profiler.timer("uncertainty_check"):
    #         answer_lower = local_result['answer'].lower()
    #         is_uncertain = any(p in answer_lower for p in [
    #             "i don't have", "no information", "i'm not aware"
    #         ])
        
    #     if not is_uncertain and local_result.get('source_documents'):
    #         print("[HYBRID] ✓ Local RAG confident")
    #         return local_result
        
    #     # Fallback to web
    #     if is_uncertain:
    #         print("[HYBRID] Uncertain, trying web...")
    #         with profiler.timer("web_search_fallback"):
    #             web_results = self.web_search(question)
            
    #         if web_results:
    #             with profiler.timer("web_answer"):
    #                 result = self._generate_web_answer(question, web_results)
                
    #             total_time = (time.perf_counter() - total_start) * 1000
    #             print(f"\n⏱️  [TOTAL_HYBRID] {total_time:.2f}ms")
    #             profiler.summary("HYBRID (Web Fallback)")
    #             return result
        
    #     print("[HYBRID] Returning local result")
    #     return local_result

    def query_with_web_fallback(
        self,
        question: str,
        force_web: bool = False,
        conversation_history: List[Dict] | None = None,
    ) -> Dict:
        """Query with smart web search fallback for out-of-scope questions"""
        
        if conversation_history is None:
            conversation_history = []
        
        profiler.reset()
        total_start = time.perf_counter()
        
        # Force web search
        if force_web:
            print("[HYBRID] 🌐 Force web search")
            with profiler.timer("web_search"):
                web_results = self.web_search(question)
            
            with profiler.timer("web_answer"):
                result = self._generate_web_answer(question, web_results)
            
            total_time = (time.perf_counter() - total_start) * 1000
            print(f"\n⏱️  [TOTAL_WEB] {total_time:.2f}ms")
            profiler.summary("WEB SEARCH PERFORMANCE")
            return result
        
        # Try local RAG first
        print("[HYBRID] Trying local RAG...")
        with profiler.timer("local_rag"):
            local_result = self.query(question, conversation_history=conversation_history)
        
        # Check if answer indicates uncertainty OR out-of-scope
        with profiler.timer("uncertainty_check"):
            answer_lower = local_result['answer'].lower()
            source_type = local_result.get('source_type', '')
            
            # Trigger web search if:
            # 1. Answer is uncertain
            # 2. OR it's an out-of-scope question
            is_uncertain = any(p in answer_lower for p in [
                "i don't have", "no information", "i'm not aware", "no specific information"
            ])
            
            is_out_of_scope = source_type == "out_of_scope_uncertain"
        
        # If confident local answer, return it
        if not is_uncertain and not is_out_of_scope and local_result.get('source_documents'):
            print("[HYBRID] ✓ Local RAG confident")
            return local_result
        
        # Fallback to web for uncertain OR out-of-scope
        if is_uncertain or is_out_of_scope:
            reason = "out-of-scope" if is_out_of_scope else "uncertain"
            print(f"[HYBRID] 🌐 Local RAG {reason}, trying web search...")
            
            with profiler.timer("web_search_fallback"):
                web_results = self.web_search(question)
            
            if web_results:
                with profiler.timer("web_answer"):
                    result = self._generate_web_answer(question, web_results)
                
                total_time = (time.perf_counter() - total_start) * 1000
                print(f"\n⏱️  [TOTAL_HYBRID] {total_time:.2f}ms")
                profiler.summary("HYBRID (Web Fallback)")
                return result
        
        # No web results, return local answer
        print("[HYBRID] Returning local result")
        return local_result

    
    # def _generate_web_answer(self, question: str, web_results: List[Dict]) -> Dict:
    #     """Generate answer from web search results"""
    #     if not web_results:
    #         return {
    #             "question": question,
    #             "answer": "I couldn't find relevant information. Please try rephrasing.",
    #             "source_documents": [],
    #             "source_type": "none"
    #         }
        
    #     web_context = "\n\n".join([
    #         f"Source: {r['title']}\n{r['content']}"
    #         for r in web_results[:3]
    #     ])
        
    #     # Reuse main prompt with web context
    #     answer = self.llm.invoke(
    #         self.prompt.format(
    #             context=web_context,
    #             question=question,
    #             chat_history=""
    #         )
    #     ).content
        
    #     return {
    #         "question": question,
    #         "answer": answer,
    #         "source_documents": web_results,
    #         "source_type": "web"
    #     }


    def _generate_web_answer(self, question: str, web_results: List[Dict]) -> Dict:
        """Generate answer from web search results with appropriate prompt"""
        if not web_results:
            return {
                "question": question,
                "answer": "I couldn't find relevant information. Please try rephrasing.",
                "source_documents": [],
                "source_type": "none"
            }
        
        # Format web context
        web_context = "\n\n".join([
            f"Source: {r['title']}\n{r['content']}"
            for r in web_results[:3]
        ])
        
        # WEB-SPECIFIC PROMPT (different from local RAG prompt)
        web_prompt = f"""You are FitMind AI, a nutrition assistant. You have access to current web search results.

    Web Search Results:
    {web_context}

    User question: {question}

    INSTRUCTIONS:
    1. The web search results above contain current, relevant information from trusted sources
    2. Use these results to provide a helpful, accurate answer
    3. You can answer questions about exercise, prices, locations, or other topics IF the web results contain that information
    4. Keep your answer concise (2-3 sentences) and cite the information from the sources
    5. If the question is about medical/exercise topics, remind users to consult appropriate professionals
    6. Always recommend consulting healthcare providers for personalized medical or fitness advice

    Answer based on the web search results:"""

        try:
            answer = self.llm.invoke(web_prompt).content
            print(f"[WEB ANSWER] Generated: {answer[:80]}...")
            
            return {
                "question": question,
                "answer": answer,
                "source_documents": web_results,
                "source_type": "web"
            }
        except Exception as e:
            print(f"[WEB ANSWER ERROR] {e}")
            return {
                "question": question,
                "answer": "I found some results but had trouble processing them. Please try again.",
                "source_documents": web_results,
                "source_type": "web"
            }
