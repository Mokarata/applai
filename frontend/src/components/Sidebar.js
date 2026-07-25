import React, { useState } from 'react';

const Sidebar = ({ jobs, onAddJobClick, onJobSelect, selectedJob, onJobsDeleted, selectedJobIds, onSelectedJobIdsChange }) => {
  const [expandedJobId, setExpandedJobId] = useState(null);
  const [activeMenuJobId, setActiveMenuJobId] = useState(null);

  const handleJobClick = (job, e) => {
    // Don't select/expand if a checkbox, button or menu was clicked
    if (e.target.closest('.job-item-checkbox, .job-item-menu, .job-item-menu-content')) {
      return;
    }
    // This function will now only handle expanding/collapsing the job details
    setExpandedJobId(prevId => (prevId === job.id ? null : job.id));
  };

  const toggleMenu = (jobId, e) => {
    e.stopPropagation(); // Prevent job item click event
    setActiveMenuJobId(prevId => (prevId === jobId ? null : jobId));
  };

  const handleRemoveJob = (jobId, e) => {
    e.stopPropagation();
    onJobsDeleted([jobId]);
    setActiveMenuJobId(null);
  };

  const handleRenameJob = (jobId, e) => {
    e.stopPropagation();
    // Placeholder for rename functionality
    alert(`Rename functionality for job ${jobId} is not yet implemented.`);
    setActiveMenuJobId(null);
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      const allJobIds = new Set(jobs.map(job => job.id));
      onSelectedJobIdsChange(allJobIds);
    } else {
      onSelectedJobIdsChange(new Set());
    }
  };

  const handleSelectJob = (jobId, e) => {
    const newSelectedJobIds = new Set(selectedJobIds);
    const jobToSelect = jobs.find(j => j.id === jobId);

    if (e.target.checked) {
      newSelectedJobIds.add(jobId);
      onJobSelect(jobToSelect); // Set this job as the active one for the chat
    } else {
      newSelectedJobIds.delete(jobId);
      // If the deselected job was the active one, clear the selection
      if (selectedJob && selectedJob.id === jobId) {
        onJobSelect(null);
      }
    }
    onSelectedJobIdsChange(newSelectedJobIds);
  };

  const handleDeleteSelected = () => {
    onJobsDeleted(Array.from(selectedJobIds));
    onSelectedJobIdsChange(new Set());
  };


  return (
    <div className="panel panel--sidebar">
      {/* Jobs Section */}
      <div className="panel-header">
        <div className="sidebar-title-container">
          <i className="material-symbols-rounded">work</i>
          <span>Jobs</span>
        </div>
        <button onClick={onAddJobClick} className="button-icon-text">+</button>
      </div>
      <div className="panel-content">
        <div className="jobs-container">
          {jobs.length > 0 && (
            <div className="selection-controls">
              <div className="select-all-container">
                <input
                  type="checkbox"
                  onChange={handleSelectAll}
                  checked={selectedJobIds.size === jobs.length && jobs.length > 0}
                  id="select-all-jobs"
                />
                <label htmlFor="select-all-jobs">Select all sources</label>
              </div>
              {selectedJobIds.size > 0 && (
                <button onClick={handleDeleteSelected} className="delete-selected-btn">
                  <i className="material-symbols-rounded">delete</i>
                  <span>Remove source</span>
                </button>
              )}
            </div>
          )}

          {jobs.length > 0 ? (
            jobs.filter(job => job).map(job => (
              <div
                key={job.id}
                className={`job-item ${selectedJob && selectedJob.id === job.id ? 'selected' : ''} ${expandedJobId === job.id ? 'expanded' : ''}`}
                onClick={(e) => handleJobClick(job, e)}
              >
                <div className="job-item-content">
                  <button className="job-item-menu" onClick={(e) => toggleMenu(job.id, e)}>
                    <i className="material-symbols-rounded">more_vert</i>
                  </button>
                  {activeMenuJobId === job.id && (
                    <div className="job-item-menu-content">
                      <button onClick={(e) => handleRenameJob(job.id, e)}>Rename</button>
                      <button onClick={(e) => handleRemoveJob(job.id, e)}>Remove</button>
                    </div>
                  )}
                  <div className="job-item-title-container">
                    {job.status === 'processing' ? (
                      <div className="skeleton-group">
                        <div className="skeleton skeleton-line w-80"></div>
                        <div className="skeleton skeleton-line w-50"></div>
                      </div>
                    ) : (
                      <>
                        <span className="job-item-title">{job.extracted_data?.title || 'Untitled'}</span><br/>
                        <span className="job-item-company">{job.extracted_data?.company_name || 'No company'}</span>
                      </>
                    )}
                  </div>
                  <input
                    type="checkbox"
                    className="job-item-checkbox"
                    checked={selectedJobIds.has(job.id)}
                    onChange={(e) => handleSelectJob(job.id, e)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
                {expandedJobId === job.id && (
                  <div className="job-item-details">
                    <p>{job.raw_text|| 'No description available.'}</p>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-content-message">No jobs added yet.</p>
          )}
        </div>
      </div>


    </div>
  );
};

export default Sidebar;
