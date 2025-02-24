import { format } from 'date-fns';

const Message = ({ text, isUserMessage, timestamp }) => {
    return (
        <div className={`flex ${isUserMessage ? 'justify-end' : 'justify-start'} mb-4`}>
            <div
                className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    isUserMessage
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                }`}
            >
                <p className="text-sm">{text}</p>
                <p className={`text-xs mt-1 ${isUserMessage ? 'text-indigo-200' : 'text-gray-500'}`}>
                    {format(new Date(timestamp), 'HH:mm')}
                </p>
            </div>
        </div>
    );
};

export default Message;