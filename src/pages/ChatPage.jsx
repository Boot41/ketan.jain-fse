import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Message from '../components/Message';
import { chatApi } from '../services/api';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const { authTokens } = useAuth();

  const handleApiError = (error) => {
    console.error('API Error:', error);
    let errorMessage = 'An unexpected error occurred. Please try again.';

    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
      } else if (error.response.status === 403) {
        errorMessage = 'You do not have permission to perform this action.';
      } else if (error.response.data && error.response.data.message) {
        errorMessage = error.response.data.message;
      }
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = 'Unable to reach the server. Please check your internet connection.';
    }

    return {
      text: errorMessage,
      isUserMessage: false,
      timestamp: new Date(),
      isError: true
    };
  };

  useEffect(() => {
    const fetchGreeting = async () => {
      try {
        const data = await chatApi.getGreeting();
        setMessages([{
          text: data.message,
          isUserMessage: false,
          timestamp: new Date(),
        }]);
      } catch (error) {
        setMessages([handleApiError(error)]);
      } finally {
        setLoading(false);
      }
    };

    fetchGreeting();
  }, []);

  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const handleSend = async () => {
    if (input.trim() && !isProcessing) {
      const userMessage = { text: input, isUserMessage: true, timestamp: new Date() };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');
      setIsProcessing(true);

      try {
        const data = await chatApi.sendMessage(input.trim(), sessionId);

        const aiMessage = {
          text: data.message,
          isUserMessage: false,
          timestamp: new Date()
        };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      } catch (error) {
        setMessages((prevMessages) => [...prevMessages, handleApiError(error)]);
      } finally {
        setIsProcessing(false);
      }
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', padding: '16px' }}>
      {loading && <div style={{ textAlign: 'center', padding: '16px' }}>Loading...</div>}
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
      </div>
      <div style={{ display: 'flex', gap: '8px', opacity: isProcessing ? 0.7 : 1 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          placeholder={isProcessing ? 'Processing...' : 'Type a message...'}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          disabled={isProcessing}
        />
        <button
          onClick={handleSend}
          style={{ padding: '8px 16px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: '#fff', cursor: isProcessing ? 'not-allowed' : 'pointer' }}
          disabled={isProcessing}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
