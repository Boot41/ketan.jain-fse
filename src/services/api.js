import axios from 'axios';

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh function
const refreshAccessToken = async (refreshToken) => {
  try {
    const response = await axios.post('/api/token/refresh/', {
      refresh: refreshToken,
    });
    return response.data.access;
  } catch (error) {
    throw new Error('Failed to refresh token');
  }
};

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const authTokens = JSON.parse(localStorage.getItem('authTokens'));
    if (authTokens?.access) {
      config.headers.Authorization = `Bearer ${authTokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const authTokens = JSON.parse(localStorage.getItem('authTokens'));
        if (!authTokens?.refresh) {
          throw new Error('No refresh token available');
        }

        // Get new access token
        const newAccessToken = await refreshAccessToken(authTokens.refresh);

        // Update tokens in localStorage
        localStorage.setItem(
          'authTokens',
          JSON.stringify({
            ...authTokens,
            access: newAccessToken,
          })
        );

        // Retry the original request with new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, clear tokens and redirect to login
        localStorage.removeItem('authTokens');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API functions
export const chatApi = {
  sendMessage: async (message, sessionId) => {
    const response = await api.post('/chat/', { message, session_id: sessionId });
    return response.data;
  },

  getGreeting: async () => {
    const response = await api.get('/greeting/');
    return response.data;
  },
};

export default chatApi;
