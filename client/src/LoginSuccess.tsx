import React from 'react';

// Define interface for component props
interface Props {
  userName?: string;
  onContinue?: () => void;
  isLoading?: boolean;
}

// Styles object for better organization and reusability
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '50vh',
    padding: '20px',
  },
  heading: {
    color: '#2c3e50',
    marginBottom: '1rem',
  },
  message: {
    color: '#34495e',
    fontSize: '1.1rem',
    marginBottom: '1.5rem',
  },
  userName: {
    color: '#16a085',
    fontWeight: 'bold',
  },
};

/**
 * LoginSuccess Component
 * Displays a success message after user login with optional user information
 *
 * @component
 * @param {Object} props - Component props
 * @param {string} props.userName - The name of the logged-in user
 * @param {Function} props.onContinue - Callback function for continue action
 * @param {boolean} props.isLoading - Loading state of the component
 */
const LoginSuccess: React.FC<Props> = ({ userName = 'Guest', onContinue, isLoading = false }) => {
  if (isLoading) {
    return (
      <main style={styles.container} role="main">
        <p>Loading...</p>
      </main>
    );
  }

  const handleContinue = () => {
    if (typeof onContinue === 'function') {
      onContinue();
    }
  };

  return (
    <main style={styles.container} role="main">
      <h1 style={styles.heading} tabIndex="0">
        Login Successful!
      </h1>
      <p style={styles.message}>
        Welcome <span style={styles.userName}>{userName}</span>! You have successfully logged in.
      </p>
      <button
        onClick={handleContinue}
        className="continue-button"
        aria-label="Continue to dashboard"
      >
        Continue to Dashboard
      </button>
    </main>
  );
};



export default LoginSuccess;
