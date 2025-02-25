import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { sendMessage, getGreeting } from '../services/api';
import MessageCard from '../components/MessageCard';
import LoadingIndicator from '../components/LoadingIndicator';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();
  const { logout } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchInitialGreeting = async () => {
      try {
        setIsLoading(true);
        const response = await getGreeting().finally(() => {
          setIsLoading(false);
        });
        setMessages([{
          type: 'assistant',
          content: response
        }]);
      } catch (error) {
        console.error('Error fetching greeting:', error);
      }
    };

    fetchInitialGreeting();
  }, []);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputMessage
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await sendMessage(inputMessage);
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: response
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        type: 'error',
        content: 'Sorry, there was an error processing your message.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm py-4 px-6 flex justify-between items-center">
        <h1 className="text-xl font-semibold text-gray-800">Jira AI Assistant</h1>
        <button
          onClick={handleLogout}
          className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900"
        >
          Logout
        </button>
      </header>

      {/* Chat Container */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <MessageCard 
              message={message.content} 
              isUserMessage={message.type === 'user'} 
              onSuggestionClick={(suggestion) => {
                setInputMessage(suggestion);
                handleSendMessage({ preventDefault: () => {} });
              }}
            />
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <LoadingIndicator />
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="p-6 bg-white border-t">
        <div className="flex space-x-4">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className={`px-6 py-2 rounded-lg bg-blue-600 text-white font-medium
              ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-blue-700'}`}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Chat;