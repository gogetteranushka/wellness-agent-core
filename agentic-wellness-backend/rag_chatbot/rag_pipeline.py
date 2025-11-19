from typing import List, Dict
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from tavily import TavilyClient
import os
from dotenv import load_dotenv
import time

load_dotenv()


class RAGPipeline:
    def __init__(
        self,
        vectorstore_path: str,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        llm_model: str = "llama3.2",
        temperature: float = 0.1,
        top_k: int = 3,
        enable_web_search: bool = True
    ):
        """Initialize RAG pipeline with web search capability"""
        
        self.vectorstore_path = vectorstore_path
        self.top_k = top_k
        
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
        
        # Initialize LLM
        print("Initializing Llama LLM...")
        self.llm = ChatOllama(
            model=llm_model,
            temperature=temperature,
            base_url="http://localhost:11434",
            request_timeout=30.0
        )
        
        # Initialize Tavily web search
        self.enable_web_search = enable_web_search
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
        
        # Create RAG chain
        self.rag_chain = (
            {"context": self.retriever | self._format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        print("RAG pipeline initialized successfully!\n")
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        """Create prompt template with relevance checking"""
        
        template = """You are FitMind AI, a nutrition assistant specializing in Indian dietary advice.

**CRITICAL**: Only use context that is RELEVANT to the user's demographic and question.
- Ignore information about different demographics (pregnant women vs men, children vs adults)
- If NO relevant information exists in context, respond with: "I don't have specific information about that in my knowledge base."

Context:
{context}

Question: {question}

Instructions:
1. Answer ONLY if context is relevant to the question's demographic/topic
2. Keep answers concise (2-3 sentences) unless detailed advice is requested
3. Admit when you don't have relevant information
4. Emphasize Indian food options when applicable
5. Recommend consulting healthcare providers for medical decisions

Answer:"""

        return ChatPromptTemplate.from_template(template)
    
    def _format_docs(self, docs: List[Document]) -> str:
        """Format retrieved documents"""
        return "\n\n".join(doc.page_content for doc in docs)
    
    # def _is_answer_uncertain(self, answer: str) -> bool:
    #     """Check if RAG answer indicates uncertainty"""
    #     answer_lower = answer.lower()
    #     uncertain_phrases = [
    #         "i don't have", "no information", "not sure",
    #         "cannot find", "no specific", "don't know",
    #         "unable to", "not available", "insufficient information",
    #         "no relevant", "cannot provide"
    #     ]
    #     return any(phrase in answer_lower for phrase in uncertain_phrases)
    def _is_answer_uncertain(self, answer: str) -> bool:
        """Enhanced uncertainty detection with pattern matching"""
        answer_lower = answer.lower()
        
        # Direct uncertainty phrases
        uncertain_phrases = [
            "i don't have", "no information", "not sure",
            "cannot find", "no specific", "don't know",
            "unable to", "not available", "insufficient information",
            "no relevant", "cannot provide", "couldn't find",
            "could not find", "not widely recognized",
            "no universally accepted", "not a widely",
            "not familiar with", "not recognized"
        ]
        
        # Check for direct matches
        if any(phrase in answer_lower for phrase in uncertain_phrases):
            return True
        
        # Check for apologetic patterns (often indicates uncertainty)
        apologetic_patterns = [
            "i can tell you that there is no",
            "however, i can tell you",
            "unfortunately",
            "i'm sorry",
            "i apologize"
        ]
        
        if any(pattern in answer_lower for pattern in apologetic_patterns):
            return True
        
        # Check if answer is very short (likely uncertain)
        if len(answer.split()) < 20:  # Less than 20 words
            return True
        
        return False
    
    def query(self, question: str) -> Dict:
        """
        Query with demographic-aware filtering
        (Your existing optimized query method - keep as is)
        """
        question_lower = question.lower()
        
        # Detect demographic and build exclusion filters
        exclude_categories = []
        
        if any(word in question_lower for word in ['male', 'man', 'men', 'boy', 'he', 'his', 'him']):
            exclude_categories.extend(['pregnant_women', 'lactating_women', 'pregnancy', 'lactation'])
        
        if any(word in question_lower for word in ['female', 'woman', 'women', 'girl', 'she', 'her']):
            if 'pregnant' not in question_lower and 'pregnancy' not in question_lower:
                exclude_categories.extend(['pregnant_women', 'pregnancy'])
        
        if any(word in question_lower for word in ['child', 'children', 'kid', 'toddler', 'infant']):
            exclude_categories.extend(['pregnant_women', 'lactating_women', 'adult'])
        
        # Retrieve documents with filtering
        try:
            if exclude_categories:
                print(f"[FILTERING] Excluding categories: {exclude_categories}")
                all_docs = self.vectorstore.similarity_search(question, k=10)
                
                filtered_docs = [
                    doc for doc in all_docs 
                    if doc.metadata.get('category', '').lower() not in [cat.lower() for cat in exclude_categories]
                    and not any(excl in doc.metadata.get('source', '').lower() for excl in ['pregnant', 'pregnancy', 'lactating'])
                ]
                
                source_docs = filtered_docs[:3] if filtered_docs else all_docs[:3]
                print(f"[FILTERING] Retrieved {len(source_docs)} relevant documents")
            else:
                source_docs = self.retriever.invoke(question)
        except Exception as e:
            print(f"[ERROR] Retrieval failed: {e}")
            source_docs = self.retriever.invoke(question)
        
        # if not source_docs:
        #     return {
        #         "question": question,
        #         "answer": "I don't have specific information about that in my knowledge base.",
        #         "source_documents": [],
        #         "source_type": "none"
        #     }
        
        # # Format context and generate answer
        # context = self._format_docs(source_docs)
        # prompt_value = self.prompt.format(context=context, question=question)
        # answer = self.llm.invoke(prompt_value).content
        
        # return {
        #     "question": question,
        #     "answer": answer,
        #     "source_documents": source_docs,
        #     "source_type": "local"
        # }
        if not source_docs:
            return {
                "question": question,
                "answer": "I don't have specific information about that in my knowledge base.",
                "source_documents": [],
                "source_type": "none"
            }
        
        # Format context and generate answer
        try:
            context = self._format_docs(source_docs)
            prompt_value = self.prompt.format(context=context, question=question)
            
            print("[LLM] Generating answer...")
            answer = self.llm.invoke(prompt_value).content
            print("[LLM] ✓ Answer generated")
            
        except TimeoutError:
            print("[LLM] ⚠ Timeout - LLM took too long")
            answer = "I don't have specific information about that in my knowledge base."
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            answer = "I don't have specific information about that in my knowledge base."
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": source_docs,
            "source_type": "local"
        }
    
    def web_search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Perform optimized web search using Tavily
        
        Args:
            query: Search query
            max_results: Maximum number of results (default: 3 for speed)
            
        Returns:
            List of search results with title, url, content
        """
        if not self.enable_web_search:
            return []
        
        try:
            start_time = time.time()
            print(f"[WEB SEARCH] Searching: {query}")
            
            # Use Tavily with optimized parameters
            response = self.tavily_client.search(
                query=query,
                max_results=max_results,
                search_depth="basic",  # Use "basic" for faster results
                include_answer=False,  # Skip AI summary for speed
                include_raw_content=False  # Skip full content for speed
            )
            
            results = []
            for result in response.get('results', []):
                results.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0)
                })
            
            elapsed = time.time() - start_time
            print(f"[WEB SEARCH] Found {len(results)} results in {elapsed:.2f}s")
            return results
        
        except Exception as e:
            print(f"[WEB SEARCH ERROR] {e}")
            return []
    
    def query_with_web_fallback(self, question: str, force_web: bool = False) -> Dict:
        """
        OPTIMIZED: Query with smart web search fallback
        
        Strategy:
        1. Try local RAG first (fast)
        2. Check if answer is confident
        3. Only trigger web search if uncertain
        
        Args:
            question: User's question
            force_web: Skip local RAG and go straight to web
            
        Returns:
            Dictionary with answer, sources, and source_type
        """
        # Force web search if requested
        if force_web:
            print("[HYBRID] Force web search mode")
            web_results = self.web_search(question)
            return self._generate_web_answer(question, web_results)
        
        # Try local RAG first (faster)
        print("[HYBRID] Trying local RAG first...")
        start_time = time.time()
        local_result = self.query(question)
        local_time = time.time() - start_time
        print(f"[HYBRID] Local RAG completed in {local_time:.2f}s")
        
        # Check if local answer is confident
        is_uncertain = self._is_answer_uncertain(local_result['answer'])
        has_sources = len(local_result.get('source_documents', [])) > 0
        
        if not is_uncertain and has_sources:
            # Local answer is good, return it
            print("[HYBRID] ✓ Local RAG answer is confident")
            return local_result
        
        # Local answer is uncertain, try web search
        print("[HYBRID] Local answer uncertain, falling back to web search...")
        web_start = time.time()
        web_results = self.web_search(question)
        web_time = time.time() - web_start
        print(f"[HYBRID] Web search completed in {web_time:.2f}s")
        
        if not web_results:
            # Web search failed, return local result anyway
            print("[HYBRID] ⚠ Web search failed, returning local result")
            return {
                **local_result,
                "source_type": "local_fallback"
            }
        
        # Generate answer from web results
        return self._generate_web_answer(question, web_results)
    
    def _generate_web_answer(self, question: str, web_results: List[Dict]) -> Dict:
        """Generate answer from web search results"""
        if not web_results:
            return {
                "question": question,
                "answer": "I couldn't find relevant information. Please try rephrasing your question.",
                "source_documents": [],
                "source_type": "none"
            }
        
        # Format web results as context
        web_context = "\n\n".join([
            f"Source: {result['title']}\n{result['content']}"
            for result in web_results[:3]  # Limit to top 3 for speed
        ])
        
        # Create web-optimized prompt
        web_prompt = f"""You are FitMind AI, a nutrition assistant. Answer the question using the web search results below.

Question: {question}

Web Search Results:
{web_context}

Instructions:
1. Provide a clear, accurate answer based on the search results
2. Keep it concise (2-3 sentences unless more detail is needed)
3. Mention this is based on current web sources
4. Recommend consulting healthcare providers for personalized medical advice

Answer:"""
        
        # Generate answer
        web_answer = self.llm.invoke(web_prompt).content
        
        return {
            "question": question,
            "answer": web_answer,
            "source_documents": web_results,
            "source_type": "web"
        }
    
    def chat(self, question: str, show_sources: bool = True) -> str:
        """Interactive chat interface with web fallback"""
        result = self.query_with_web_fallback(question)
        
        response = f"Question: {result['question']}\n\n"
        response += f"Answer: {result['answer']}\n"
        response += f"Source: {result.get('source_type', 'unknown')}\n"
        
        if show_sources and result.get('source_documents'):
            response += f"\n{'='*60}\nSources:\n"
            
            if result.get('source_type') == 'web':
                for i, doc in enumerate(result['source_documents'], 1):
                    response += f"\n{i}. {doc.get('title', 'N/A')}\n"
                    response += f"   URL: {doc.get('url', 'N/A')}\n"
                    response += f"   {doc.get('content', '')[:150]}...\n"
            else:
                for i, doc in enumerate(result['source_documents'], 1):
                    response += f"\n{i}. {doc.metadata['source']} (Category: {doc.metadata['category']})\n"
                    response += f"   {doc.page_content[:150]}...\n"
        
        return response
    
    def query_with_history(self, question: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Query with conversation history for context retention
        
        Args:
            question: Current user question
            conversation_history: List of previous Q&A pairs in format:
                [{"question": "...", "answer": "..."}, ...]
                
        Returns:
            Dict with question, answer, source_documents, and source_type
        """
        if conversation_history is None:
            conversation_history = []
        
        # Build conversation context from history
        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            history_text = "PREVIOUS CONVERSATION:\n"
            # Use last 3 exchanges to keep context manageable
            for exchange in conversation_history[-3:]:
                if isinstance(exchange, dict):
                    # Handle both formats: {"question": "...", "answer": "..."} or {"role": "...", "content": "..."}
                    if "question" in exchange and "answer" in exchange:
                        history_text += f"User: {exchange['question'][:200]}\n"
                        history_text += f"Assistant: {exchange['answer'][:200]}\n\n"
                    elif "role" in exchange and "content" in exchange:
                        role = "User" if exchange["role"] == "user" else "Assistant"
                        history_text += f"{role}: {exchange['content'][:200]}\n\n"
            history_text += "---\n\n"
        
        # Detect if we should use web search based on question
        if self._should_use_web_search(question):
            print("[HISTORY] Question routed to web search (location/brand/recent)")
            web_results = self.web_search(question)
            result = self._generate_web_answer(question, web_results)
            result["conversation_history_used"] = len(conversation_history) > 0
            return result
        
        # Use local RAG with history context
        question_lower = question.lower()
        
        # Apply demographic filtering
        exclude_categories = []
        if any(word in question_lower for word in ['male', 'man', 'men', 'boy', 'he', 'his', 'him']):
            exclude_categories.extend(['pregnant_women', 'lactating_women', 'pregnancy', 'lactation'])
        
        if any(word in question_lower for word in ['female', 'woman', 'women', 'girl', 'she', 'her']):
            if 'pregnant' not in question_lower and 'pregnancy' not in question_lower:
                exclude_categories.extend(['pregnant_women', 'pregnancy'])
        
        # Retrieve documents
        try:
            if exclude_categories:
                print(f"[FILTERING] Excluding categories: {exclude_categories}")
                all_docs = self.vectorstore.similarity_search(question, k=10)
                filtered_docs = [
                    doc for doc in all_docs 
                    if doc.metadata.get('category', '').lower() not in [cat.lower() for cat in exclude_categories]
                    and not any(excl in doc.metadata.get('source', '').lower() for excl in ['pregnant', 'pregnancy', 'lactating'])
                ]
                source_docs = filtered_docs[:3] if filtered_docs else all_docs[:3]
            else:
                source_docs = self.retriever.invoke(question)
        except Exception as e:
            print(f"[ERROR] Retrieval failed: {e}")
            source_docs = self.retriever.invoke(question)
        
        if not source_docs:
            return {
                "question": question,
                "answer": "I don't have specific information about that in my knowledge base.",
                "source_documents": [],
                "source_type": "none",
                "conversation_history_used": len(conversation_history) > 0
            }
        
        # Format context with history
        docs_context = self._format_docs(source_docs)
        full_context = history_text + "KNOWLEDGE BASE:\n" + docs_context
        
        # Generate answer with history context
        try:
            prompt_value = self.prompt.format(context=full_context, question=question)
            print("[LLM] Generating answer with conversation history...")
            answer = self.llm.invoke(prompt_value).content
            print("[LLM] ✓ Answer generated")
            
            # Check if answer is uncertain
            if self._is_answer_uncertain(answer):
                print("[HISTORY] Local answer uncertain, falling back to web search...")
                web_results = self.web_search(question)
                if web_results:
                    result = self._generate_web_answer(question, web_results)
                    result["conversation_history_used"] = len(conversation_history) > 0
                    return result
        
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            answer = "I'm experiencing technical difficulties. Please try again."
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": source_docs,
            "source_type": "local",
            "conversation_history_used": len(conversation_history) > 0
        }
    
    def _should_use_web_search(self, question: str) -> bool:
        """
        Determine if question should route directly to web search
        
        Args:
            question: User's question
            
        Returns:
            True if question should use web search, False otherwise
        """
        question_lower = question.lower()
        
        # Location-specific queries
        location_keywords = [
            "restaurant", "cafe", "café", "location", "where", "place",
            "bangalore", "delhi", "mumbai", "chennai", "hyderabad",
            "pune", "kolkata", "address", "near me", "recommend a place",
            "store", "shop", "market"
        ]
        
        # Brand/product specific queries
        brand_keywords = [
            "brand", "product name", "buy", "purchase",
            "glucon", "horlicks", "boost", "complan",
            "amazon", "flipkart"
        ]
        
        # Current/recent information
        time_keywords = [
            "latest", "recent", "2025", "2024", "2023",
            "current", "new", "updated", "today",
            "this year", "this month"
        ]
        
        # Check if any trigger keywords are present
        if any(keyword in question_lower for keyword in location_keywords):
            return True
        
        if any(keyword in question_lower for keyword in brand_keywords):
            return True
        
        if any(keyword in question_lower for keyword in time_keywords):
            return True
        
        return False