import React, { useState } from 'react';
import axios from '../axiosInstance'; // Axios setup for HTTP requests
import { useNavigate } from 'react-router-dom'; // For page redirection

const SignIn = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Handle input changes
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // Submit form data
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
        console.log(formData)
      const response = await axios.post('/signin/',formData);
      localStorage.setItem('username', response.data.username); 
      localStorage.setItem('email', response.data.email);
      localStorage.setItem('token', response.data.token);  // Save access token
      localStorage.setItem('refresh_token', response.data.refresh_token);  // Save refresh token
      navigate('/home'); // Redirect to dashboard
    } catch (err) {
      setError(err.response?.data?.message || 'SignIn failed'); // Show error
    }
  };

  return (
    <div className="flex flex-col items-center mt-6 lg:mt-20">
      <div className="p-10 border border-neutral-700 rounded-xl w-80">
        <h2 className="text-3xl sm:text-3xl lg:text-4xl text-center tracking-wide bg-gradient-to-r from-orange-500 to-red-800 text-transparent bg-clip-text">
          SignIn 

        </h2>
        
        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {/* Email Input */}
          <input
            type="email"
            name="email"
            placeholder="Email"
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />

          {/* Password Input */}
          <input
            type="password"
            name="password"
            placeholder="Password"
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-neutral-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          />

          {/* Submit Button */}
          <button
            type="submit"
            className="inline-flex justify-center items-center text-center w-full h-12 px-6 text-lg font-medium text-white bg-orange-700 hover:bg-orange-800 border border-orange-700 rounded-lg transition duration-200"
          >
            SignIn
          </button>
        </form>
        </div>
        <a href="https://chat-persona-ai-ov46.vercel.app/google_login">
          <button
            className="mt-4 flex items-center justify-center w-80 h-12 border border-orange-700 rounded-lg shadow-sm hover:shadow-md transition duration-200 bg-transparent text-white font-medium"
          >
            <img 
              src="https://www.svgrepo.com/show/355037/google.svg" 
              alt="Google Logo" 
              className="w-6 h-6 mr-3"
            />
            Sign in with Google
          </button>
        </a>
        
          
    </div>
  );

};

export default SignIn;