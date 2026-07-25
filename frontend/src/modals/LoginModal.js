import React, { useState } from 'react';
import * as api from '../services/api';

const LoginModal = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.login(email, password);
      onLoginSuccess();
    } catch (err) {
      setError('Failed to log in. Please check your credentials.');
      console.error(err);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '400px' }}>
        <div className="modal-header">
          <h2 className="modal-title">Login</h2>
        </div>
        <div className="modal-body">
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label htmlFor="email">Email or Username</label>
              <input
                type="text"
                id="email"
                className="form-control"
                placeholder="Enter your email or username"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                className="form-control"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="error-message" style={{color: 'red', marginBottom: '1rem'}}>{error}</p>}
            <div className="modal-footer" style={{paddingTop: 0, borderTop: 'none'}}>
              <button type="submit" className="btn-primary">Login</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;
