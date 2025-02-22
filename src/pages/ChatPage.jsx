import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import Message from '../components/Message';
import axios from 'axios';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const { authTokens } = useAuth();

  useEffect(() => {
    const fetchGreeting = async () => {
      try {
        const response = await axios.get('/api/greeting/', {
          headers: {
            'Authorization': `Bearer ${authTokens.access}`,
          },
        });
        setMessages([{
          text: response.data.message,
          isUserMessage: false,
          timestamp: new Date(),
        }]);
      } catch (error) {
        console.error('Failed to fetch greeting:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGreeting();
  }, [authTokens]);

  const [isProcessing, setIsProcessing] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  const handleSend = async () => {
    if (input.trim() && !isProcessing) {
      const userMessage = { text: input, isUserMessage: true, timestamp: new Date() };
      setMessages((prevMessages) => [...prevMessages, userMessage]);
      setInput('');
      setIsProcessing(true);

      try {
        const response = await axios.post('/api/chat/', {
          message: input.trim(),
          session_id: sessionId
        }, {
          headers: {
            'Authorization': `Bearer ${authTokens.access}`,
            'Content-Type': 'application/json'
          }
        });

        const aiMessage = {
          text: response.data.message,
          isUserMessage: false,
          timestamp: new Date()
        };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      } catch (error) {
        console.error('Failed to send message:', error);
        // Add error message to chat
        const errorMessage = {
          text: 'Sorry, there was an error processing your message. Please try again.',
          isUserMessage: false,
          timestamp: new Date(),
          isError: true
        };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
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
