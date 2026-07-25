import React, { useState, useEffect } from 'react';
import Dropdown from './Dropdown';
import SettingsModal from './SettingsModal';
import * as api from '../services/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatContainer = ({ user, jobs, selectedJob, selectedJobIds, onLetterGenerated }) => {
  const [messages, setMessages] = useState([]);
  const userInitials = user ? `${(user.first_name || '').charAt(0)}${(user.last_name || '').charAt(0)}`.toUpperCase() : 'U';
  const [chatInput, setChatInput] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [style, setStyle] = useState('Default');
  const [length, setLength] = useState('Medium');
  const [language, setLanguage] = useState('English');
  const [model, setModel] = useState('GPT-4');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(1024);
  const [sessionId, setSessionId] = useState(null); // State for the chat session ID
  const [isGenerating, setIsGenerating] = useState(false);
  const [abortController, setAbortController] = useState(null);

  // Effect to start a new chat session when a job is selected
  useEffect(() => {
    const startNewSession = async (job) => {
      try {
        const newSessionId = crypto.randomUUID();
        setSessionId(newSessionId);

        const initialMessageText = 
          job.extracted_data?.job_summary || 
          `Starting a new chat for ${job.extracted_data?.title || 'the selected job'}. How can I help you refine the cover letter?`;

        const initialMessage = {
          sender: 'ai',
          text: initialMessageText,
          timestamp: new Date().toISOString(),
        };

        // Set the message locally for immediate display
        setMessages([initialMessage]);

        // Also send this initial message to the backend to seed the history
        await api.sendChatMessage(newSessionId, null, initialMessageText);
        console.log(`New chat session started and seeded: ${newSessionId}`);
      } catch (error) {
        console.error('Failed to start or seed new chat session:', error);
        setMessages([{
          sender: 'ai',
          text: 'Sorry, I could not start a new chat session. Please try again.'
        }]);
      }
    };

    if (selectedJob) {
      startNewSession(selectedJob);
    } else {
      setSessionId(null);
      setMessages([]);
    }
  }, [selectedJob]);

  const toggleSettings = () => setIsSettingsOpen(!isSettingsOpen);

  const handleGenerateCoverLetter = async () => {
    if (selectedJobIds.size !== 1 || isGenerating) {
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
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);

    const controller = new AbortController();
    setAbortController(controller);
    setIsGenerating(true);

    try {
      const options = { style, length, language, model, temperature, max_tokens: maxTokens };
      const result = await api.generateCoverLetter(selectedJob.id, options, controller.signal);

      if (result && result.text) {
        const aiMessage = {
          sender: 'ai',
          text: result.text,
          isCoverLetter: true,
          isUnsaved: true,
          letterData: result,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, aiMessage]);
      } else if (result) { // Handle cases where there might not be text but the request was not aborted
        throw new Error('The server returned an empty or invalid response.');
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Cover letter generation aborted');
        const aiMessage = { sender: 'ai', text: 'Cover letter generation stopped.', timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          sender: 'ai',
          text: `Sorry, I couldn't generate the cover letter. Error: ${error.message}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsGenerating(false);
      setAbortController(null);
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
          id: savedLetter.id,
          letterData: savedLetter,
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

  const handleStopGenerating = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim() || isGenerating) return;

    const userMessage = { sender: 'user', text: chatInput, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    const currentInput = chatInput;
    setChatInput('');

    // If no job is selected, provide guidance and stop.
    if (!selectedJob || !sessionId) {
      const aiMessage = {
        sender: 'ai',
        text: 'Please select a job to start chatting about the cover letter.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMessage]);
      return;
    }

    // If a job is selected, proceed to call the API.
    const controller = new AbortController();
    setAbortController(controller);
    setIsGenerating(true);

    try {
      // Find the last AI message in the history to provide as context
      const lastMessage = messages.length > 0 ? messages[messages.length - 1] : null;
      const lastAiMessage = lastMessage && lastMessage.sender === 'ai' ? lastMessage.text : null;

      const result = await api.sendChatMessage(sessionId, currentInput, lastAiMessage, controller.signal);
      if (result) {
        const aiMessage = { sender: 'ai', text: result.bot_response, timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Request aborted');
        const aiMessage = { sender: 'ai', text: 'Message generation stopped.', timestamp: new Date().toISOString() };
        setMessages(prev => [...prev, aiMessage]);
      } else {
        const errorMessage = {
          sender: 'ai',
          text: `Sorry, I couldn't get a response. Error: ${error.message}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } finally {
      setIsGenerating(false);
      setAbortController(null);
    }
  };

  return (
    <div className="panel chat-container">
      <div className="panel-header">
        <span>Chat</span>
        <button className="button-icon" onClick={toggleSettings}>
          <i className="material-symbols-rounded">tune</i>
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
            messages.map((msg, index) => {
              const prev = messages[index - 1];
              const showAvatar = !prev || prev.sender !== msg.sender;
              const timeLabel = msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';
              return (
                <div key={index} className={`message-row ${msg.sender} ${showAvatar ? '' : 'compact'}`}>
                  {showAvatar ? (
                    <div className={`avatar ${msg.sender === 'ai' ? 'avatar--ai' : 'avatar--user'}`}>
                      {msg.sender === 'ai' ? (
                        <i className="material-symbols-rounded">smart_toy</i>
                      ) : (
                        <span>{userInitials}</span>
                      )}
                    </div>
                  ) : (
                    <div className="avatar-spacer" />
                  )}
                  <div className={`message ${msg.sender}`}>
                    {msg.sender === 'ai' ? (
                      <ReactMarkdown className="markdown" remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                    ) : (
                      <p style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                    )}
                    <div className="message-meta">
                      {timeLabel && <span className="timestamp">{timeLabel}</span>}
                    </div>
                    {msg.isCoverLetter && (
                      <div className="message-actions">
                        <button className="button-icon" onClick={() => handleRate(msg.id, 'good')}><i className="material-symbols-rounded">thumb_up</i></button>
                        <button className="button-icon" onClick={() => handleRate(msg.id, 'bad')}><i className="material-symbols-rounded">thumb_down</i></button>
                        {msg.isUnsaved && (
                          <button className="button-secondary" onClick={() => handleSaveCoverLetter(msg.letterData, index)}>Save</button>
                        )}
                        <button className="button-secondary" onClick={(e) => handleCopy(msg.text, e)}>Copy</button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="empty-chat">
              <i className="material-symbols-rounded">edit_note</i>
              <h2>{selectedJob ? selectedJob.extracted_data?.title : 'Untitled notebook'}</h2>
              <p>{selectedJob ? 'Generate a cover letter or start chatting to refine it.' : 'Select a job to begin.'}</p>
            </div>
          )}
        </div>
        
        <div className="chat-omnibar">
          {/* Quick options chips (NotebookLM style) */}
          <div className="quick-options">
            <div className="quick-options-buttons">
              <button className="quick-option-btn" onClick={() => setChatInput(prev => (prev ? prev + ' Summarize the job posting in 5 bullets.' : 'Summarize the job posting in 5 bullets.'))}>
                <i className="material-symbols-rounded">bolt</i> Summarize job
              </button>
              <button className="quick-option-btn" onClick={() => setChatInput(prev => (prev ? prev + ' Draft a concise intro paragraph for this cover letter.' : 'Draft a concise intro paragraph for this cover letter.'))}>
                <i className="material-symbols-rounded">lightbulb</i> Draft intro
              </button>
              <button className="quick-option-btn" onClick={() => setChatInput(prev => (prev ? prev + ' Extract the top 5 required skills from this job.' : 'Extract the top 5 required skills from this job.'))}>
                <i className="material-symbols-rounded">list_alt</i> Extract skills
              </button>
              <button className="quick-option-btn" onClick={() => setChatInput(prev => (prev ? prev + ' Tailor the letter to this company’s mission and products.' : 'Tailor the letter to this company’s mission and products.'))}>
                <i className="material-symbols-rounded">target</i> Tailor to company
              </button>
            </div>
          </div>

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
              disabled={selectedJobIds.size !== 1 || isGenerating}
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
            {isGenerating ? (
              <button id="stop-button" className="stop-button" onClick={handleStopGenerating}>
                <i className="material-symbols-rounded">stop</i>
              </button>
            ) : (
              <button id="send-button" className="chat-button" onClick={handleSendMessage} disabled={!chatInput.trim()}>
                <i className="material-symbols-rounded">send</i>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;
