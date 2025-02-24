import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken'));
    const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken'));
    const [isAuthenticated, setIsAuthenticated] = useState(!!accessToken);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (accessToken) {
            localStorage.setItem('accessToken', accessToken);
            setIsAuthenticated(true);
        } else {
            localStorage.removeItem('accessToken');
            setIsAuthenticated(false);
        }
    }, [accessToken]);

    useEffect(() => {
        if (refreshToken) {
            localStorage.setItem('refreshToken', refreshToken);
        } else {
            localStorage.removeItem('refreshToken');
        }
    }, [refreshToken]);

    const login = async (username, password) => {
        try {
            const response = await axios.post(`${API_URL}/token/`, { username, password });
            const { access, refresh } = response.data;
            setAccessToken(access);
            setRefreshToken(refresh);
            setIsAuthenticated(true);
            setError(null);
            return true;
        } catch (err) {
            setError(err.response?.data?.error || 'Login failed');
            setIsAuthenticated(false);
            return false;
        }
    };

    const logout = () => {
        setAccessToken(null);
        setRefreshToken(null);
        setIsAuthenticated(false);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
    };

    const refreshAccessToken = async () => {
        try {
            const response = await axios.post(`${API_URL}/token/refresh/`, {
                refresh: refreshToken
            });
            setAccessToken(response.data.access);
            return true;
        } catch (err) {
            logout();
            return false;
        }
    };

    const value = {
        isAuthenticated,
        login,
        logout,
        refreshAccessToken,
        error,
        accessToken
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};