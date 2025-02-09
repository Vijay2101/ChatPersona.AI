import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const AuthRedirectPage = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Get query parameters from the URL
    const params = new URLSearchParams(window.location.search);

    // Extract user data from the URL
    const name = params.get('name');
    const email = params.get('email');
    const token = params.get('token');
    const refreshToken = params.get('refresh_token');

    if (name && email && token && refreshToken) {
      // Store data in localStorage
      localStorage.setItem('username', name);
      localStorage.setItem('email', email);
      localStorage.setItem('token', token); // Save access token
      localStorage.setItem('refresh_token', refreshToken); // Save refresh token

      // Redirect to home page after saving the data
      navigate('/home');
    } else {
      console.error("Error: Missing required query parameters");
    }
  }, [navigate]);

  return (
    <div>
      <p>Redirecting...</p>
    </div>
  );
};

export default AuthRedirectPage;
