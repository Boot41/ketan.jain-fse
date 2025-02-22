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

  const handleSend = async () => {
    if (input.trim()) {
      const newMessage = { text: input, isUserMessage: true, timestamp: new Date() };
      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInput('');

      // Simulate AI response (to be replaced with actual OpenAI integration)
      setTimeout(() => {
        const aiMessage = { text: 'This is a simulated AI response.', isUserMessage: false, timestamp: new Date() };
        setMessages((prevMessages) => [...prevMessages, aiMessage]);
      }, 1000);
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
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
          placeholder="Type a message..."
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
        />
        <button
          onClick={handleSend}
          style={{ padding: '8px 16px', borderRadius: '4px', border: 'none', backgroundColor: '#007bff', color: '#fff' }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
