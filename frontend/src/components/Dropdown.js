import React, { useState, useEffect, useRef } from 'react';

const Dropdown = ({ label, options, selected, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleSelect = (option) => {
    onSelect(option);
    setIsOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  return (
    <div className="dropdown-container" ref={dropdownRef}>
      <button className="button-secondary dropdown-toggle" onClick={() => setIsOpen(!isOpen)}>
        {label}: {selected}
        <i className="material-icons">{isOpen ? 'arrow_drop_up' : 'arrow_drop_down'}</i>
      </button>
      {isOpen && (
        <div className="dropdown-menu">
          {options.map((option) => (
            <button 
              key={option}
              className={`dropdown-item ${selected === option ? 'selected' : ''}`}
              onClick={() => handleSelect(option)}
            >
              {option}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dropdown;
