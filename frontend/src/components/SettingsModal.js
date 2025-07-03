import React from 'react';
import Dropdown from './Dropdown';

const SettingsModal = ({ 
  isOpen, 
  onClose, 
  style, setStyle, 
  length, setLength, 
  language, setLanguage,
  model, setModel,
  temperature, setTemperature,
  maxTokens, setMaxTokens
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Configure Chat</h2>
          <button className="button-icon" onClick={onClose}>
            <i className="material-icons">close</i>
          </button>
        </div>
        <div className="modal-body">
          <p>Adjust the model parameters and generation settings for this chat.</p>
          
          <div className="settings-grid">
            {/* LLM Settings */}
            <div className="setting-item">
              <label>LLM Model</label>
              <Dropdown 
                label="Model"
                options={['GPT-4', 'GPT-3.5-Turbo', 'Claude 3 Sonnet']}
                selected={model}
                onSelect={setModel}
              />
            </div>
            <div className="setting-item">
              <label>Temperature: {temperature}</label>
              <input 
                type="range" 
                min="0" 
                max="1" 
                step="0.1" 
                value={temperature} 
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
              />
            </div>
            <div className="setting-item">
              <label>Max Output Tokens</label>
              <input 
                type="number" 
                className="input-field"
                value={maxTokens} 
                onChange={(e) => setMaxTokens(parseInt(e.target.value, 10))}
              />
            </div>

            {/* Generation Settings */}
            <div className="setting-item">
              <label>Style</label>
              <Dropdown 
                label="Style"
                options={['Default', 'Professional', 'Casual', 'Enthusiastic']}
                selected={style}
                onSelect={setStyle}
              />
            </div>
            <div className="setting-item">
              <label>Length</label>
              <Dropdown 
                label="Length"
                options={['Short', 'Medium', 'Long']}
                selected={length}
                onSelect={setLength}
              />
            </div>
            <div className="setting-item">
              <label>Language</label>
              <Dropdown 
                label="Language"
                options={['English', 'Spanish', 'French', 'German']}
                selected={language}
                onSelect={setLanguage}
              />
            </div>
          </div>
        </div>
        <div className="modal-footer">
          <button className="button-secondary" onClick={onClose}>Cancel</button>
          <button className="button-primary" onClick={onClose}>Save Changes</button>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;
