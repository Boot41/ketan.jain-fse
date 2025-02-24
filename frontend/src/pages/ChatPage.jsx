import { useState, useEffect, useRef } from 'react';
import { sendMessage, getGreeting } from '../services/api';
import Message from '../components/Message';

const ChatPage = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const fetchGreeting = async () => {
            try {
                const response = await getGreeting();
                setMessages([{
                    text: response.message,
                    isUserMessage: false,
                    timestamp: new Date().toISOString()
                }]);
            } catch (err) {
                setError('Failed to load initial greeting');
            }
        };

        fetchGreeting();
    }, []);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            text: inputMessage,
            isUserMessage: true,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await sendMessage(inputMessage);

            setMessages(prev => [...prev, {
                text: response.message,
                isUserMessage: false,
                timestamp: new Date().toISOString()
            }]);
        } catch (err) {
            setError('Failed to send message. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-50">
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-white">
                {messages.map((message, index) => (
                    <Message
                        key={index}
                        text={message.text}
                        isUserMessage={message.isUserMessage}
                        timestamp={message.timestamp}
                    />
                ))}
                {error && (
                    <div className="text-red-500 text-center py-2 bg-red-50 rounded-md">
                        {error}
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-100 bg-white shadow-sm">
                <div className="flex space-x-4 max-w-4xl mx-auto">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Type your message..."
                        className="flex-1 p-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-50"
                        disabled={isLoading}
                    />
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors duration-200"
                    >
                        {isLoading ? 'Sending...' : 'Send'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default ChatPage;