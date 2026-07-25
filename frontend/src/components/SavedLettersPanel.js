import React, { useState } from 'react';

const SavedLettersPanel = ({ coverLetters, onCoverLetterSelect, selectedCoverLetter, onCoverLettersDeleted }) => {
  const [expandedLetterId, setExpandedLetterId] = useState(null);
  const [selectedLetterIds, setSelectedLetterIds] = useState(new Set());
  const [activeMenuLetterId, setActiveMenuLetterId] = useState(null);

  const handleLetterClick = (letter, e) => {
    if (e.target.closest('.job-item-checkbox, .job-item-menu, .job-item-menu-content')) {
      return;
    }
    onCoverLetterSelect(letter);
    setExpandedLetterId(prevId => (prevId === letter.id ? null : letter.id));
  };

  const toggleMenu = (letterId, e) => {
    e.stopPropagation();
    setActiveMenuLetterId(prevId => (prevId === letterId ? null : letterId));
  };

  const handleRemoveLetter = (letterId, e) => {
    e.stopPropagation();
    onCoverLettersDeleted([letterId]);
    setActiveMenuLetterId(null);
  };

  const handleRenameLetter = (letterId, e) => {
    e.stopPropagation();
    alert(`Rename functionality for letter ${letterId} is not yet implemented.`);
    setActiveMenuLetterId(null);
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      const allLetterIds = new Set(coverLetters.map(letter => letter.id));
      setSelectedLetterIds(allLetterIds);
    } else {
      setSelectedLetterIds(new Set());
    }
  };

  const handleSelectLetter = (letterId, e) => {
    const newSelectedLetterIds = new Set(selectedLetterIds);
    if (e.target.checked) {
      newSelectedLetterIds.add(letterId);
    } else {
      newSelectedLetterIds.delete(letterId);
    }
    setSelectedLetterIds(newSelectedLetterIds);
  };

  const handleDeleteSelected = () => {
    onCoverLettersDeleted(Array.from(selectedLetterIds));
    setSelectedLetterIds(new Set());
  };

  return (
    <div className="panel panel--right">
      <div className="panel-header">
        <div className='sidebar-title-container'>
          <i className="material-symbols-rounded">archive</i>
          <span>Saved Letters</span>
        </div>
      </div>
      <div className="panel-content">
        <div className="jobs-container"> 
          {coverLetters && coverLetters.length > 0 && (
            <div className="selection-controls">
              <div className="select-all-container">
                <input
                  type="checkbox"
                  onChange={handleSelectAll}
                  checked={selectedLetterIds.size === coverLetters.length && coverLetters.length > 0}
                  id="select-all-letters"
                />
                <label htmlFor="select-all-letters">Select all letters</label>
              </div>
              {selectedLetterIds.size > 0 && (
                <button onClick={handleDeleteSelected} className="delete-selected-btn">
                  <i className="material-symbols-rounded">delete</i>
                  <span>Remove selected</span>
                </button>
              )}
            </div>
          )}
          {coverLetters && coverLetters.length > 0 ? (
            coverLetters.map(letter => (
              <div
                key={letter.id}
                className={`job-item ${selectedCoverLetter && selectedCoverLetter.id === letter.id ? 'selected' : ''} ${expandedLetterId === letter.id ? 'expanded' : ''}`}
                onClick={(e) => handleLetterClick(letter, e)}
              >
                <div className="job-item-content">
                  <button className="job-item-menu" onClick={(e) => toggleMenu(letter.id, e)}>
                    <i className="material-symbols-rounded">more_vert</i>
                  </button>
                  {activeMenuLetterId === letter.id && (
                    <div className="job-item-menu-content">
                      <button onClick={(e) => handleRenameLetter(letter.id, e)}>Rename</button>
                      <button onClick={(e) => handleRemoveLetter(letter.id, e)}>Remove</button>
                    </div>
                  )}
                  <div className="job-item-title-container">
                    <span className="job-item-title">{letter.title || 'Untitled Letter'}</span><br/>
                  </div>
                  <input
                    type="checkbox"
                    className="job-item-checkbox"
                    checked={selectedLetterIds.has(letter.id)}
                    onChange={(e) => handleSelectLetter(letter.id, e)}
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
                {expandedLetterId === letter.id && (
                  <div className="job-item-details">
                    <p>{letter.raw_text || 'No content available.'}</p>
                  </div>
                )}
              </div>
            ))
          ) : (
            <p className="no-content-message">No cover letters saved yet.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default SavedLettersPanel;
