import axiosInstance from './axiosConfig';

interface ApiResponse<T> {
    data?: T;
    error?: string;
}

export const getHelloWorld = async (): Promise<ApiResponse<string>> => {
    try {
        const response = await axiosInstance.get('/api/hello/');
        return { data: response.data.message };
    } catch (error: any) {
        return {
            error: error.response?.data?.detail || 'Failed to fetch hello world message',
        };
    }
};

// Add more API endpoints here as needed
