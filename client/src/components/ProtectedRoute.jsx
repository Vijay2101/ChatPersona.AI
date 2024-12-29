import React from 'react';
import { Navigate } from 'react-router-dom'; // Use Navigate instead of Redirect
import { Outlet } from 'react-router-dom'; // Outlet is used for nested routes

const ProtectedRoute = () => {
  const token = localStorage.getItem('token'); // Check if token exists

  return token ? <Outlet /> : <Navigate to="/" />; // Redirect to signin if no token
};

export default ProtectedRoute;
