import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar'

import HomePage from './pages/HomePage';
import LandingPage from './pages/LandingPage';
import ChatbotPage from './pages/ChatbotPage';
import ChatPage from './pages/ChatPage';
const App = () => {
  return (
    <Router>
    
      <Navbar />


      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/chatbot" element={<ChatbotPage />} />
        <Route path="/chat" element={<ChatPage />} />
        {/* Define other routes here */}
      </Routes>
    </Router>
  );
};

export default App
