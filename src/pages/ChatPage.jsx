import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const ChatPage = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const { authTokens } = useAuth();

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
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px' }}>
        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              textAlign: message.isUserMessage ? 'right' : 'left',
              marginBottom: '8px',
              padding: '8px',
              backgroundColor: message.isUserMessage ? '#007bff' : '#f1f1f1',
              color: message.isUserMessage ? '#fff' : '#000',
              borderRadius: '8px',
              maxWidth: '70%',
              alignSelf: message.isUserMessage ? 'flex-end' : 'flex-start',
            }}
          >
            {message.text}
            <div style={{ fontSize: '12px', color: message.isUserMessage ? '#ddd' : '#666', marginTop: '4px' }}>
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
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
