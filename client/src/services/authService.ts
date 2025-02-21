import axiosInstance from './axiosConfig';

interface LoginResponse {
    access: string;
    refresh: string;
}

interface AuthError {
    message: string;
}

export const login = async (email: string, password: string): Promise<LoginResponse | AuthError> => {
    try {
        const response = await axiosInstance.post('/api/token/', {
            email,
            password,
        });

        const { access, refresh } = response.data;
        
        // Store tokens
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        
        return response.data;
    } catch (error: any) {
        return {
            message: error.response?.data?.detail || 'Login failed. Please try again.',
        };
    }
};

export const refreshToken = async (): Promise<string | null> => {
    try {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) return null;

        const response = await axiosInstance.post('/api/token/refresh/', {
            refresh,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        
        return access;
    } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        return null;
    }
};

export const logout = (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    // Clear any other auth-related state
    window.location.href = '/login';
};

export const isAuthenticated = (): boolean => {
    return !!localStorage.getItem('access_token');
};
