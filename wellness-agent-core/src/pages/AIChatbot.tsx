import Chatbot from '../components/Chatbot';

export default function AIChatbot() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-indigo-100 to-pink-100 p-4">
      <div className="max-w-6xl mx-auto h-[calc(100vh-2rem)]">
        <Chatbot />
      </div>
    </div>
  );
}
