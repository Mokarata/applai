import React, { useState } from 'react';
import * as api from '../services/api';

const AddJobModal = ({ onClose, onJobAdded, userId }) => {
  const [activeSource, setActiveSource] = useState('url');
  const [jobUrl, setJobUrl] = useState('');
  const [jobText, setJobText] = useState('');
  const [jobFile, setJobFile] = useState(null);
  const [manual, setManual] = useState({ title: '', company: '', description: '' });

      const handleAddJob = async () => {
    try {
      const formData = new FormData();

      switch (activeSource) {
        case 'url':
          if (!jobUrl) {
            alert('Please enter a job URL.');
            return;
          }
          formData.append('source_url', jobUrl);
          break;
        case 'text':
          if (!jobText) {
            alert('Please enter the job text.');
            return;
          }
          formData.append('source_text', jobText);
          break;
        case 'manual':
          if (!manual.description) {
            alert('Please enter a job description.');
            return;
          }
          // The backend extracts job details from the source text.
          formData.append('source_text', manual.description);
          break;
        case 'file':
          if (!jobFile) {
            alert('Please select a file to upload.');
            return;
          }
          // The backend endpoint expects the file under the key 'source_files'.
          formData.append('source_files', jobFile);
          break;
        default:
          console.error('Invalid active source:', activeSource);
          return;
      }

      // All job creation requests go through the same API call with FormData.
            const newJob = await api.addJob(formData);
      
      // Pass the newly created job back to App.js
      onJobAdded(newJob);
      onClose();

    } catch (error) {
      console.error('Failed to add job:', error);
      // Optionally, display an error message to the user
    }
  };
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Add a New Job</h2>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <div className="source-options">
          <button className={`source-option ${activeSource === 'url' ? 'active' : ''}`} onClick={() => setActiveSource('url')}>
            <i className="material-symbols-rounded">link</i> Via URL
          </button>
          <button className={`source-option ${activeSource === 'text' ? 'active' : ''}`} onClick={() => setActiveSource('text')}>
            <i className="material-symbols-rounded">article</i> Via Text
          </button>
          <button className={`source-option ${activeSource === 'file' ? 'active' : ''}`} onClick={() => setActiveSource('file')}>
            <i className="material-symbols-rounded">upload_file</i> Via File
          </button>
          <button className={`source-option ${activeSource === 'manual' ? 'active' : ''}`} onClick={() => setActiveSource('manual')}>
            <i className="material-symbols-rounded">edit_square</i> Manual
          </button>
        </div>
        <div className="source-panels">
          <div id="source-url" className={`source-panel ${activeSource === 'url' ? 'active' : ''}`}>
            <div className="form-group">
              <label htmlFor="job-url-input">Job Posting URL</label>
              <input type="url" id="job-url-input" className="form-control" placeholder="https://www.linkedin.com/jobs/view/..." value={jobUrl} onChange={e => setJobUrl(e.target.value)} />
            </div>
          </div>
          <div id="source-text" className={`source-panel ${activeSource === 'text' ? 'active' : ''}`}>
            <div className="form-group">
              <label htmlFor="job-text-input">Job Posting Text</label>
              <textarea id="job-text-input" className="form-control" placeholder="Paste the job description here..." value={jobText} onChange={e => setJobText(e.target.value)}></textarea>
            </div>
          </div>
          <div id="source-file" className={`source-panel ${activeSource === 'file' ? 'active' : ''}`}>
            <div className="form-group">
              <label htmlFor="job-file-input">Upload Job Description File</label>
              <input type="file" id="job-file-input" className="form-control" onChange={e => setJobFile(e.target.files[0])} />
            </div>
          </div>
          <div id="source-manual" className={`source-panel ${activeSource === 'manual' ? 'active' : ''}`}>
            <div className="form-group">
              <label htmlFor="manual-job-title">Job Title</label>
              <input type="text" id="manual-job-title" className="form-control" placeholder="Software Engineer" value={manual.title} onChange={e => setManual({...manual, title: e.target.value})} />
            </div>
            <div className="form-group">
              <label htmlFor="manual-job-company">Company Name</label>
              <input type="text" id="manual-job-company" className="form-control" placeholder="Innovate Inc." value={manual.company} onChange={e => setManual({...manual, company: e.target.value})} />
            </div>
            <div className="form-group">
              <label htmlFor="manual-job-description">Job Description</label>
              <textarea id="manual-job-description" className="form-control" placeholder="Enter job description..." value={manual.description} onChange={e => setManual({...manual, description: e.target.value})}></textarea>
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="btn-primary" onClick={handleAddJob}>Add Job</button>
        </div>
      </div>
    </div>
  );
};

export default AddJobModal;
