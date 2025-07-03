import React, { useState, useEffect } from 'react';

const UserProfileModal = ({ user, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    resume_text: '',
  });
  const [fileName, setFileName] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim(),
        email: user.email || '',
        phone: user.phone_number || '',
        resume_text: user.resume_text || '',
      });
      setFileName(''); // Reset file name when modal opens/user changes
    }
  }, [user]);

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({ ...prev, [id]: value }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) {
      setFileName('');
      return;
    }

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (event) => {
      setFormData(prev => ({ ...prev, resume_text: event.target.result }));
    };
    reader.onerror = () => {
      console.error('Could not read file.');
      setFileName('Error reading file.');
    };
    reader.readAsText(file);
  };

  const handleSave = () => {
    onSave(formData);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2 className="modal-title">User Profile</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <div className="profile-section">
          <div className="form-group">
            <label htmlFor="full-name">Full Name</label>
            <input type="text" id="full_name" className="form-control" placeholder="Enter your full name" value={formData.full_name} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input type="email" id="email" className="form-control" placeholder="Enter your email" value={formData.email} onChange={handleChange} />
          </div>
          <div className="form-group">
            <label htmlFor="phone">Phone</label>
            <input type="tel" id="phone" className="form-control" placeholder="Enter your phone number" value={formData.phone} onChange={handleChange} />
          </div>
        </div>
        <div className="profile-section">
          <div className="form-group">
            <label htmlFor="resume-text">Paste your resume text</label>
            <textarea id="resume_text" className="form-control" placeholder="Paste your resume text here..." value={formData.resume_text} onChange={handleChange}></textarea>
          </div>
          <div className="form-group">
            <label>Or upload your resume</label>
            <div className="file-upload">
              <p>{fileName || 'Drag & drop or click to upload file'}</p>
              <input type="file" id="resume-file-input" onChange={handleFileChange} accept=".txt,.md" />
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-primary" onClick={handleSave}>Save Profile</button>
        </div>
      </div>
    </div>
  );
};

export default UserProfileModal;
