import axios from 'axios';

// Create a base Axios instance
const axiosInstance = axios.create({
  baseURL: 'https://chat-persona-ai-ov46.vercel.app/', // Your Django Backend URL
  headers: {
    'Content-Type': 'application/json', // Default header for JSON
  },
});

// Function to refresh the token
const refreshToken = async () => {
  const refresh_token = localStorage.getItem('refresh_token'); // Get refresh token from localStorage
  if (!refresh_token) {
    throw new Error("No refresh token found");
  }

  try {
    // Make a request to the backend to get a new access token using the refresh token
    const response = await axios.post('https://chat-persona-ai-ov46.vercel.app/refresh_token', {
      refresh_token: refresh_token,
    });

    const { access_token, refresh_token: newRefreshToken } = response.data;
    
    // Store the new tokens in localStorage
    localStorage.setItem('token', access_token);
    localStorage.setItem('refresh_token', newRefreshToken);

    return access_token; // Return the new access token
  } catch (error) {
    console.error("Error refreshing token:", error);
    // Handle any error related to token refresh (log the user out or show a message)
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/'; // Redirect to login page
    throw error; // Rethrow the error
  }
};

// Add an interceptor to handle authorization and token refresh
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token'); // Get access token from localStorage
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`; // Add token to headers if available
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add an interceptor to handle responses and refresh token if needed
axiosInstance.interceptors.response.use(
  (response) => response, // If response is successful, just return it
  async (error) => {
    const originalRequest = error.config;

    // If we get a 401 Unauthorized error and the request is not a retry
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;  // Mark the request as a retry

      try {
        // Try to refresh the token
        const newAccessToken = await refreshToken();

        // Retry the original request with the new access token
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        return axios(originalRequest); // Retry the original request
      } catch (refreshError) {
        // If refreshing the token fails, redirect to login page or show an error message
        return Promise.reject(refreshError);
      }
    }

    // If it's not a 401 error or we've already tried refreshing, reject the error
    return Promise.reject(error);
  }
);

export default axiosInstance;
