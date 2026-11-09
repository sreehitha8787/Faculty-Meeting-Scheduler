import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../api';
import muWordmark from '../assets/MU_Wordmark_Transparent.webp';
import '../App.css';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [helpMessage, setHelpMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setHelpMessage('');
    setIsLoading(true);
    try {
      // Sign in with the unique university staff username, not an email address.
      const response = await api.post('/login/', { username: username.trim(), password });
      const data = response.data;
      if (!data.token || !data.profile?.user?.username) {
        throw new Error('The server did not return a valid login session. Please contact the administrator.');
      }
      localStorage.setItem('auth_token', data.token);
      localStorage.setItem('username', data.profile.user.username);
      localStorage.setItem('profile', JSON.stringify(data.profile));
      navigate(location.state?.from?.pathname || '/home', { replace: true });
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Unable to log in. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="login-page login-page-reference">
      <div className="login-site-shell">
        <header className="login-site-header">
          <img className="login-site-logo" src={muWordmark} alt="Mahindra University — Global Thinkers, Engaged Leaders" />
          <div className="login-site-subtitle">Staff workspace</div>
        </header>
        <section className="login-content-area" aria-labelledby="login-title">
          <div className="login-box login-box-reference">
            <div className="login-reference-content">
              <div className="login-eyebrow">STAFF ACCESS</div>
              <h1 id="login-title">Welcome back</h1>
              <p className="login-intro">Sign in with your unique university staff username.</p>
              <form onSubmit={handleSubmit}>
                <label className="login-field-label" htmlFor="username">Username</label>
                <input
                  className="login-reference-input"
                  id="username"
                  name="username"
                  autoComplete="username"
                  required
                  placeholder="Enter your staff username"
                  aria-label="Username"
                  value={username}
                  onChange={(event) => setUsername(event.target.value)}
                />
                <p className="login-field-hint">Use your username, not your email address.</p>
                <label className="login-field-label" htmlFor="password">Password</label>
                <div className="login-password-row">
                  <input
                    className="login-reference-input"
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    placeholder="Enter your password"
                    aria-label="Password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                  />
                  <button className="login-password-toggle" type="button" onClick={() => setShowPassword((shown) => !shown)} aria-label={showPassword ? 'Hide password' : 'Show password'} title={showPassword ? 'Hide password' : 'Show password'}>
                    {showPassword ? (
                      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M9.9 5.2A10.7 10.7 0 0112 5c5.2 0 8.5 5 8.5 5a13 13 0 01-3 3.4M6.2 6.3C3.8 7.8 2 10 2 10s3.3 5 10 5c.9 0 1.7-.1 2.5-.4" /></svg>
                    ) : (
                      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.3-6 10-6 10 6 10 6-3.3 6-10 6-10-6-10-6z" /><circle cx="12" cy="12" r="2.7" /></svg>
                    )}
                  </button>
                </div>
                {error && <div className="login-reference-error" role="alert">{error}</div>}
                <button type="submit" className="login-btn login-reference-btn" disabled={isLoading}>
                  {isLoading ? 'Signing in…' : 'Sign in'}
                </button>
              </form>
              <p className="login-footnote">Secure access for Mahindra University staff.</p>
              <button type="button" className="login-forgot-link" onClick={() => setHelpMessage('For password assistance, please contact your university administrator.')}>Forgot password?</button>
              {helpMessage && <p className="login-forgot-help" role="status">{helpMessage}</p>}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
