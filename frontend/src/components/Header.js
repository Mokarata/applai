import React from 'react';

const Header = ({ user, onProfileClick, onLogout, isAuthenticated }) => {
  return (
    <header className="app-header">
      <div className="app-title">
        <i className="material-symbols-rounded">description</i>
        <span>AI Cover Letter Generator</span>
      </div>

      <div className="header-center">
        <div className="header-searchbar">
          <i className="material-symbols-rounded">search</i>
          <input type="text" placeholder="Search…" aria-label="Search" />
        </div>
      </div>

      <div className="header-actions">
        {isAuthenticated && (
          <>
            <button className="profile-button" onClick={onProfileClick}>
              <i className="material-symbols-rounded">person</i>
            </button>
            <button className="logout-button" onClick={onLogout}>Logout</button>
          </>
        )}
      </div>
    </header>
  );
};

export default Header;
