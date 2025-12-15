import { useState, useRef, useEffect } from 'react';

interface Message {
  type: 'user' | 'bot';
  content: string;
  sources?: Source[];
}

interface Source {
  source: string;
  category: string;
  content: string;
}

// NEW: Correct format for conversation history
interface ConversationExchange {
  question: string;
  answer: string;
}

const EXAMPLE_QUESTIONS = [
  'What should a diabetic patient eat for breakfast?',
  'How to reduce blood pressure through diet?',
  'Best protein sources for vegetarians?',
  'Foods to avoid for heart disease?',
];

const API_URL = 'http://localhost:8000';

export default function Chatbot() {
  const [messages, setMessages] = useState<Message[]>([
    {
      type: 'bot',
      content: '👋 Hello! I\'m FitMind AI, your nutrition assistant. Ask me anything about Indian dietary guidelines, managing health conditions through diet, or personalized meal planning!',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // UPDATED: Use correct format for conversation history
  const [conversationHistory, setConversationHistory] = useState<ConversationExchange[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async (question?: string) => {
    const messageText = question || input.trim();
    
    if (!messageText) return;

    const userMessage: Message = { type: 'user', content: messageText };
    setMessages((prev) => [...prev, userMessage]);
    
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: messageText,
          show_sources: true,
          // UPDATED: Send in correct format
          conversation_history: conversationHistory.slice(-3),  // Send last 3 Q&A pairs
          use_web_search: null  // Auto mode
        }),
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();
      const botMessage: Message = {
        type: 'bot',
        content: data.answer,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, botMessage]);
      
      // UPDATED: Store in correct format (question + answer pair)
      setConversationHistory(prev => [
        ...prev,
        {
          question: messageText,
          answer: data.answer
        }
      ]);
      
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        type: 'bot',
        content: '❌ Sorry, I encountered an error. Please make sure the backend API is running at http://localhost:8000',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 text-center">
        <h1 className="text-2xl font-bold mb-1">🥗 FitMind AI Nutrition Chat</h1>
        <p className="text-sm opacity-90">Your Personal Nutrition Assistant for Indian Dietary Guidance</p>
      </div>

      {/* Example Questions */}
      <div className="flex flex-wrap gap-2 p-4 bg-gray-50 border-b">
        {EXAMPLE_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => sendMessage(q)}
            className="px-3 py-1.5 text-xs bg-white border border-gray-300 rounded-full hover:bg-purple-600 hover:text-white hover:border-purple-600 transition-all duration-200"
          >
            {q.split('?')[0]}?
          </button>
        ))}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[70%] rounded-2xl p-4 ${
                msg.type === 'user'
                  ? 'bg-purple-600 text-white rounded-br-md'
                  : 'bg-white text-gray-800 rounded-bl-md shadow-md'
              }`}
            >
              <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>

              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <h4 className="text-sm font-semibold mb-2 text-purple-600">📚 Sources:</h4>
                  <div className="space-y-2">
                    {msg.sources.map((src, i) => (
                      <div key={i} className="text-xs bg-gray-50 p-2 rounded">
                        <strong>{i + 1}. {src.source}</strong>
                        <span className="text-gray-500"> ({src.category})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl p-4 shadow-md">
              <div className="flex space-x-2">
                {[0, 150, 300].map((delay, i) => (
                  <div
                    key={i}
                    className="w-2 h-2 bg-purple-600 rounded-full animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask about nutrition, diet plans, or health conditions..."
            className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-full focus:border-purple-600 focus:outline-none transition-colors"
            disabled={loading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-full font-semibold hover:shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
