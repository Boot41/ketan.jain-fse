import React from 'react';
import PropTypes from 'prop-types';

const Message = ({ message }) => {
  const messageStyle = {
    textAlign: message.isUserMessage ? 'right' : 'left',
    marginBottom: '8px',
    padding: '8px',
    backgroundColor: message.isUserMessage ? '#007bff' : '#f1f1f1',
    color: message.isUserMessage ? '#fff' : '#000',
    borderRadius: '8px',
    maxWidth: '70%',
    alignSelf: message.isUserMessage ? 'flex-end' : 'flex-start',
    display: 'inline-block',
  };

  const timestampStyle = {
    fontSize: '12px',
    color: message.isUserMessage ? '#ddd' : '#666',
    marginTop: '4px',
  };

  return (
    <div style={{ display: 'flex', justifyContent: message.isUserMessage ? 'flex-end' : 'flex-start' }}>
      <div style={messageStyle}>
        {message.text}
        <div style={timestampStyle}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

Message.propTypes = {
  message: PropTypes.shape({
    text: PropTypes.string.isRequired,
    isUserMessage: PropTypes.bool.isRequired,
    timestamp: PropTypes.instanceOf(Date).isRequired,
  }).isRequired,
};

export default Message;
