import { format } from 'date-fns';

// Text Message Component
const TextMessage = ({ content }) => (
  <div className="p-4 bg-white rounded-lg shadow-sm">
    <p>{content}</p>
  </div>
);

const GreetingMessage = ({ message, suggestions, onSuggestionClick }) => (
  <div className="space-y-4">
    <div className="p-4 bg-white rounded-lg shadow-sm">
      <p>{message}</p>
    </div>
    {suggestions && suggestions.length > 0 && (
      <div className="space-y-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            className="w-full p-3 text-left bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            onClick={() => onSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>
    )}
  </div>
);

// Issue List Component
const IssueList = ({ issues, summary }) => (
  <div className="space-y-4">
    <p className="text-gray-700">{summary}</p>
    <div className="space-y-2">
      {issues.map((issue, index) => (
        <div key={index} className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="flex justify-between items-start">
            <span className="text-blue-600 font-medium">{issue.key}</span>
            <span className="px-2 py-1 text-sm rounded-full bg-gray-100">{issue.status}</span>
          </div>
          <h3 className="font-medium mt-2">{issue.summary}</h3>
          <p className="text-sm text-gray-600 mt-2 line-clamp-2">{issue.description}</p>
          <div className="flex justify-between items-center mt-3 text-sm text-gray-500">
            <span>Priority: {issue.priority}</span>
            <span>{format(new Date(issue.created), 'MMM d, yyyy')}</span>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Single Issue Component
const Issue = ({ issue, summary }) => (
  <div className="space-y-4">
    <p className="text-gray-700">{summary}</p>
    <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-start">
        <span className="text-blue-600 font-medium">{issue.key}</span>
        <span className="px-2 py-1 text-sm rounded-full bg-gray-100">{issue.status}</span>
      </div>
      <h3 className="font-medium mt-2">{issue.summary}</h3>
      <p className="text-sm text-gray-600 mt-2">{issue.description}</p>
      <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
        <div>
          <span className="text-gray-500">Assignee:</span> {issue.assignee}
        </div>
        <div>
          <span className="text-gray-500">Reporter:</span> {issue.reporter}
        </div>
        <div>
          <span className="text-gray-500">Priority:</span> {issue.priority}
        </div>
        <div>
          <span className="text-gray-500">Created:</span> {format(new Date(issue.created), 'MMM d, yyyy')}
        </div>
      </div>
      {issue.comments && issue.comments.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <h4 className="font-medium mb-2">Comments</h4>
          <div className="space-y-3">
            {issue.comments.map((comment, index) => (
              <div key={index} className="text-sm">
                <div className="flex justify-between items-center text-gray-500">
                  <span>{comment.author}</span>
                  <span>{format(new Date(comment.created), 'MMM d, yyyy HH:mm')}</span>
                </div>
                <p className="mt-1">{comment.body}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  </div>
);

// Comment Component
const Comment = ({ comment, summary }) => (
  <div className="space-y-4">
    <p className="text-gray-700">{summary}</p>
    <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>{comment.author}</span>
        <span>{format(new Date(comment.created), 'MMM d, yyyy HH:mm')}</span>
      </div>
      <p className="mt-2">{comment.body}</p>
    </div>
  </div>
);

// Status List Component
const StatusList = ({ statuses, summary }) => (
  <div className="space-y-4">
    <p className="text-gray-700">{summary}</p>
    <div className="grid gap-2">
      {statuses.map((status, index) => (
        <div key={index} className="p-4 bg-white rounded-lg shadow-sm border border-gray-200">
          <h3 className="font-medium">{status.name}</h3>
          <p className="text-sm text-gray-600 mt-1">{status.description}</p>
        </div>
      ))}
    </div>
  </div>
);

// User List Component
const UserList = ({ users, summary }) => (
  <div className="space-y-4">
    <p className="text-gray-700">{summary}</p>
    <div className="grid gap-2">
      {users.map((user, index) => (
        <div key={index} className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 flex justify-between items-center">
          <div>
            <h3 className="font-medium">{user.display_name}</h3>
            <p className="text-sm text-gray-600">{user.email}</p>
          </div>
          <span className={`px-2 py-1 text-sm rounded-full ${user.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
            {user.active ? 'Active' : 'Inactive'}
          </span>
        </div>
      ))}
    </div>
  </div>
);

// Main Message Card Component
const MessageCard = ({ message, isUserMessage, onSuggestionClick }) => {
  const renderContent = () => {
    if (isUserMessage) {
      return <p>{message}</p>;
    }

    switch (message.type) {
      case 'text':
        return <TextMessage content={message.content} />;
      case 'issue_list':
        return <IssueList issues={message.issues} summary={message.summary} />;
      case 'issue':
        return <Issue issue={message.issue} summary={message.summary} />;
      case 'comment':
        return <Comment comment={message.comment} summary={message.summary} />;
      case 'status_list':
        return <StatusList statuses={message.statuses} summary={message.summary} />;
      case 'user_list':
        return <UserList users={message.users} summary={message.summary} />;
      case 'status_update':
        return <StatusUpdate result={message.result} summary={message.summary} />;
      case 'new_issue':
        return <NewIssue issue={message.issue} summary={message.summary} />;
      case 'greeting':
        return <GreetingMessage message={message.message} suggestions={message.suggestions} onSuggestionClick={onSuggestionClick} />;
      default:
        return <p>Unsupported message type</p>;
    }
  };

  return (
    <div className={`flex ${isUserMessage ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[70%] rounded-lg ${isUserMessage 
          ? 'bg-blue-600 text-white p-4'
          : 'bg-transparent'}`}
      >
        {renderContent()}
      </div>
    </div>
  );
};

export default MessageCard;