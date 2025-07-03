import React, { useState } from 'react';
import Dropdown from './Dropdown';
import SettingsModal from './SettingsModal'; // Import the new modal component
import * as api from '../services/api';

const USER_ID = 1; // Hardcoded for now

const ChatContainer = ({ user, jobs, selectedJob, selectedJobIds, onLetterGenerated }) => {
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false); // This will be repurposed for the modal
  const [style, setStyle] = useState('Default');
  const [length, setLength] = useState('Medium');
  const [language, setLanguage] = useState('English');
  const [model, setModel] = useState('GPT-4');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1024);

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  const handleGenerateCoverLetter = async () => {
    if (selectedJobIds.size !== 1) {
      alert('Please select exactly one job to generate a cover letter.');
      return;
    }

    const selectedJobId = selectedJobIds.values().next().value;
    const selectedJob = jobs.find(job => job.id === selectedJobId);

    if (!selectedJob) {
      alert('Could not find the selected job. Please try again.');
      return;
    }

    const userMessage = {
      sender: 'user',
      text: `Generate a cover letter for the ${selectedJob.extracted_data?.title || 'selected job'} position...`,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const options = { style, length, language, model, temperature, max_tokens: maxTokens };
      const result = await api.generateCoverLetter(selectedJob.id, options);

      if (result && result.text) {
        // Add the unsaved letter to the chat
        const aiMessage = {
          sender: 'ai',
          text: result.text,
          isCoverLetter: true,
          isUnsaved: true, // Flag to show the 'Save' button
          letterData: result, // Store the full data needed for saving
        };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error('The server returned an empty or invalid response.');
      }
    } catch (error) {
      const errorMessage = {
        sender: 'ai',
        text: `Sorry, I couldn't generate the cover letter. Error: ${error.message}`,
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleCopy = (text, e) => {
    navigator.clipboard.writeText(text).then(() => {
      const button = e.currentTarget;
      button.textContent = 'Copied!';
      setTimeout(() => {
        button.textContent = 'Copy';
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy text: ', err);
    });
  };

  const handleRate = (letterId, rating) => {
    // Placeholder for rating functionality
    console.log(`Rated letter ${letterId} with ${rating}`);
  };

  const handleSaveCoverLetter = async (letterDataToSave, messageIndex) => {
    try {
      const savedLetter = await api.saveCoverLetter(letterDataToSave);
      
      // Update the specific message in the state to remove the save button
      setMessages(prevMessages => {
        const newMessages = [...prevMessages];
        const savedMessage = {
          ...newMessages[messageIndex],
          isUnsaved: false,
          id: savedLetter.id, // Update with the real ID from the DB
          letterData: savedLetter, // Update with the full saved data
        };
        newMessages[messageIndex] = savedMessage;
        return newMessages;
      });

      // Notify the parent component to refresh the list of saved letters
      onLetterGenerated();
      
      console.log(`Successfully saved letter ${savedLetter.id}`);

    } catch (error) {
      console.error('Failed to save cover letter:', error);
      alert(`Failed to save cover letter: ${error.message}`);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { sender: 'user', text: chatInput };
    setMessages(prev => [...prev, userMessage]);
    setChatInput('');

    try {
      // This assumes a generic chat API endpoint exists
      const selectedJobId = selectedJobIds.values().next().value;
      const selectedJob = jobs.find(job => job.id === selectedJobId);
      const result = await api.generateResponse(USER_ID, selectedJob.id, chatInput);
      const aiMessage = { sender: 'ai', text: result.response_text };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'ai',
        text: `Sorry, I couldn't generate a response. Error: ${error.message}`
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="panel chat-container">
      <div className="panel-header">
        <span>Chat</span>
        <button className="button-icon" onClick={toggleSettings}>
          <i className="material-icons">tune</i>
        </button>
      </div>

      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={toggleSettings}
        style={style} setStyle={setStyle}
        length={length} setLength={setLength}
        language={language} setLanguage={setLanguage}
        model={model} setModel={setModel}
        temperature={temperature} setTemperature={setTemperature}
        maxTokens={maxTokens} setMaxTokens={setMaxTokens}
      />

      <div className="panel-content chat-content-area">
        <div id="chat-messages" className="chat-messages">
          {messages.length > 0 ? (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                {msg.isCoverLetter && (
                  <div className="message-actions">
                    <button className="button-icon" onClick={() => handleRate(msg.id, 'good')}><i className="material-icons">thumb_up</i></button>
                    <button className="button-icon" onClick={() => handleRate(msg.id, 'bad')}><i className="material-icons">thumb_down</i></button>
                    {msg.isUnsaved && (
                      <button className="button-secondary" onClick={() => handleSaveCoverLetter(msg.letterData, index)}>Save</button>
                    )}
                    <button className="button-secondary" onClick={(e) => handleCopy(msg.text, e)}>Copy</button>
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="empty-chat">
              <i className="material-icons">edit_note</i>
              <h2>{selectedJob ? selectedJob.extracted_data?.title : 'Untitled notebook'}</h2>
              <p>{selectedJob ? 'Generate a cover letter to get started.' : 'Select a job to begin.'}</p>
            </div>
          )}
        </div>
        
        <div className="chat-omnibar">
          <div className="omnibar-options">
            <Dropdown 
              label="Style"
              options={['Default', 'Professional', 'Casual', 'Enthusiastic']}
              selected={style}
              onSelect={setStyle}
            />
            <Dropdown 
              label="Length"
              options={['Short', 'Medium', 'Long']}
              selected={length}
              onSelect={setLength}
            />
            <Dropdown 
              label="Language"
              options={['English', 'Spanish', 'French', 'German']}
              selected={language}
              onSelect={setLanguage}
            />
            <button 
              className="button-primary"
              onClick={handleGenerateCoverLetter}
              disabled={selectedJobIds.size !== 1}
            >
              Generate cover letter
            </button>
          </div>
          <div className="chat-input-container">
            <textarea 
              id="chat-input" 
              className="chat-input" 
              placeholder="Or, type a prompt to refine the letter..." 
              value={chatInput} 
              onChange={e => setChatInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
            />
            <button id="send-button" className="chat-button" onClick={handleSendMessage}>
              <i className="material-icons">send</i>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
