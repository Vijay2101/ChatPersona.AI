import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'; // Import ProtectedRoute component
import HomePage from './pages/HomePage';
import LandingPage from './pages/LandingPage';
import ChatbotPage from './pages/ChatbotPage';
import ChatPage from './pages/ChatPage';
AuthRedirectPage
import AuthRedirectPage from './pages/AuthRedirectPage';
import SignInPage from './pages/SignInPage';
import SignUpPage from './pages/SignUpPage';
const App = () => {
  return (
    <Router>
    
      


      <Routes>
        <Route path="/" element={<LandingPage />} />
        {/* <Route path="/home" element={<HomePage />} /> */}
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/chatbot" element={<ChatbotPage />} />
          <Route path="/chat" element={<ChatPage />} />
        </Route>
        
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/AuthRedirectPage" element={<AuthRedirectPage />} />
        <Route path="*" element={<LandingPage />} />
        {/* Define other routes here */}
      </Routes>
    </Router>
  );
};

export default App
