import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = localStorage.getItem('auth_token');

  if (!token) {
    return <Navigate to="/" replace state={{ from: location }} />;
  }

  return children;
}
