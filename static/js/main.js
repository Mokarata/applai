/**
 * AI Cover Letter Generator - UI Functionality
 * Handles panel expansion/collapse, modals, and API interactions
 */

document.addEventListener('DOMContentLoaded', function() {
  // API client using vanilla Fetch API
  const API_BASE_URL = '/api';
  
  // Job API methods - using Fetch API
  const jobsApi = {
    // Get all jobs
    getAllJobs: async function() {
      try {
        // Fetch returns a Promise
        const response = await fetch(`${API_BASE_URL}/jobs/`);
        
        // Check if request was successful
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        // Parse JSON response
        const data = await response.json();
        console.log('Fetched jobs:', data);
        return data;
      } catch (error) {
        console.error('Error fetching jobs:', error);
        return [];
      }
    },
    
    // Delete a job
    deleteJob: async function(jobId) {
      try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
          method: 'DELETE',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return true; // Successful deletion
      } catch (error) {
        console.error(`Error deleting job ${jobId}:`, error);
        throw error;
      }
    },
    
    // Create a new job
    createJob: async function(jobData) {
      try {
        const response = await fetch(`${API_BASE_URL}/jobs/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(jobData) // Convert JS object to JSON string
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json(); // Return the created job
      } catch (error) {
        console.error('Error creating job:', error);
        throw error;
      }
    },
    
    // Upload a job file
    uploadJobFile: async function(formData) {
      try {
        const response = await fetch(`${API_BASE_URL}/jobs/upload`, {
          method: 'POST',
          body: formData // FormData is sent as-is (no JSON.stringify)
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error('Error uploading job file:', error);
        throw error;
      }
    }
  };
  
  // Cover Letter API methods
  const coverLettersApi = {
    // Generate a cover letter
    generateCoverLetter: async function(userId, jobId, templateName = 'standard') {
      try {
        const response = await fetch(`${API_BASE_URL}/cover-letters/?user_id=${userId}&job_id=${jobId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            template_name: templateName,
            cover_letter_text: null  // Let the backend generate this
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json(); // Return the created cover letter
      } catch (error) {
        console.error('Error generating cover letter:', error);
        throw error;
      }
    },
    
    // Get a cover letter by ID
    getCoverLetter: async function(coverLetterId) {
      try {
        const response = await fetch(`${API_BASE_URL}/cover_letters/${coverLetterId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
      } catch (error) {
        console.error(`Error fetching cover letter ${coverLetterId}:`, error);
        throw error;
      }
    },
    
    // Delete a cover letter
    deleteCoverLetter: async function(coverLetterId) {
      try {
        const response = await fetch(`${API_BASE_URL}/cover_letters/${coverLetterId}`, {
          method: 'DELETE',
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return true; // Successful deletion
      } catch (error) {
        console.error(`Error deleting cover letter ${coverLetterId}:`, error);
        throw error;
      }
    }
  };
  
  // User API methods
  const userApi = {
    // Get user profile
    getUserProfile: async function(userId = 1) {
      try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
      } catch (error) {
        console.error('Error fetching user profile:', error);
        return null;
      }
    },
    
    // Update user profile
    updateUserProfile: async function(userId, userData) {
      try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(userData)
        });
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.json();
      } catch (error) {
        console.error('Error updating user profile:', error);
        throw error;
      }
    }
  };
  
  // DOM Elements with corrected IDs
  const profileBtn = document.getElementById('profile-btn');
  const profileModal = document.getElementById('profile-modal');
  const closeProfileBtn = document.getElementById('close-profile-modal'); // Fixed ID
  const saveProfileBtn = document.getElementById('save-profile-btn');
  const addJobBtn = document.getElementById('add-job-btn');
  const addJobModal = document.getElementById('add-job-modal');
  const closeJobBtn = document.getElementById('close-job-modal');
  const addJobSubmit = document.getElementById('add-job-submit');
  const cancelJobBtn = document.getElementById('cancel-job-btn');
  const panels = document.querySelectorAll('.panel');
  const panelHeaders = document.querySelectorAll('.panel-header');
  const jobsList = document.getElementById('jobs-list');
  const resumeUpload = document.getElementById('resume-upload');
  const resumeFile = document.getElementById('resume-file');
  const resumeFileName = document.getElementById('resume-file-name');
  const jobFileUpload = document.getElementById('job-file-upload');
  const jobFile = document.getElementById('job-file');
  const jobFileName = document.getElementById('job-file-name');
  const sendMessageBtn = document.getElementById('send-message-btn');
  const chatInput = document.getElementById('chat-input');
  const chatMessages = document.getElementById('chat-messages');
  const saveLetterBtn = document.getElementById('save-letter-btn');
  const sourceOptions = document.querySelectorAll('.source-option');
  const sourcePanels = document.querySelectorAll('.source-panel');
  const emptyJobsState = document.getElementById('empty-jobs-state');
  const emptySavedState = document.getElementById('empty-saved-state');
  const generateCoverLetterBtn = document.getElementById('generate-cover-letter-btn');
  const customizeLetterBtn = document.getElementById('customize-letter-btn');
  const highlightSkillsBtn = document.getElementById('highlight-skills-btn');
  const formalToneBtn = document.getElementById('formal-tone-btn');
  const suggestedPrompts = document.querySelectorAll('.suggested-prompt');
  
  // State
  let userProfile = {
    id: 1, // Default user ID
    fullName: '',
    email: '',
    phone: '',
    resume: ''
  };
  
  // Initialize with empty jobs array that will be populated from API
  let jobs = [];
  let currentLetter = null;
  let savedLetters = [];
  
  // Panel expand/collapse - fixing inconsistent class handling
  panelHeaders.forEach(header => {
    header.addEventListener('click', function() {
      const panel = this.parentElement;
      const isExpanded = panel.classList.contains('expanded');
      
      // First collapse all panels
      panels.forEach(p => p.classList.remove('expanded'));
      
      // Then expand the clicked one if it wasn't already expanded
      if (!isExpanded) {
        panel.classList.add('expanded');
      }
    });
  });
  
  // Modal functionality - using classList for consistency with original design
  profileBtn.addEventListener('click', async () => {
    profileModal.classList.add('active');
    await loadUserProfile();
  });
  
  closeProfileBtn.addEventListener('click', () => {
    profileModal.classList.remove('active');
  });
  
  addJobBtn.addEventListener('click', () => {
    addJobModal.classList.add('active');
  });
  
  // Close job modal function
  function closeJobModal() {
    addJobModal.classList.remove('active');
    
    // Reset form fields - safely check if elements exist before resetting
    const urlInput = document.getElementById('job-url');
    if (urlInput) urlInput.value = '';
    
    const jobTextInput = document.getElementById('job-text');
    if (jobTextInput) jobTextInput.value = '';
    
    // Reset manual panel fields
    const manualTitleInput = document.getElementById('job-title');
    if (manualTitleInput) manualTitleInput.value = '';
    
    const manualCompanyInput = document.getElementById('job-company');
    if (manualCompanyInput) manualCompanyInput.value = '';
    
    const manualDescInput = document.getElementById('job-description');
    if (manualDescInput) manualDescInput.value = '';
    
    // Reset file input
    if (jobFile) {
      jobFile.value = '';
      if (jobFileName) {
        jobFileName.style.display = 'none';
      }
    }
  }
  
  closeJobBtn.addEventListener('click', closeJobModal);
  if (cancelJobBtn) {
    cancelJobBtn.addEventListener('click', closeJobModal);
  }
  
  // Close modals when clicking outside content
  window.addEventListener('click', (e) => {
    if (e.target === profileModal) {
      profileModal.classList.remove('active');
    }
    if (e.target === addJobModal) {
      closeJobModal();
    }
  });
  
  // File upload handling
  resumeUpload.addEventListener('click', () => {
    resumeFile.click();
  });
  
  resumeFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const fileName = e.target.files[0].name;
      resumeFileName.textContent = fileName;
      resumeFileName.style.display = 'block';
    }
  });
  
  jobFileUpload.addEventListener('click', () => {
    jobFile.click();
  });
  
  jobFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      const fileName = e.target.files[0].name;
      jobFileName.textContent = fileName;
      jobFileName.style.display = 'block';
    }
  });
  
  // Source option handling for job input method selection
  // IMPORTANT: This replaces the old tab handling code
  sourceOptions.forEach(option => {
    option.addEventListener('click', function() {
      const panelId = this.getAttribute('data-panel');
      
      // Update active state for options
      sourceOptions.forEach(opt => opt.classList.remove('active'));
      this.classList.add('active');
      
      // Update active state for panels
      sourcePanels.forEach(panel => {
        if (panel.id === panelId) {
          panel.classList.add('active');
        } else {
          panel.classList.remove('active');
        }
      });
      
      console.log(`Selected panel: ${panelId}`); // Debug log
    });
  });
  
  // Chat functionality
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
  
  sendMessageBtn.addEventListener('click', sendMessage);
  
  function sendMessage() {
    const message = chatInput.value.trim();
    if (message) {
      addUserMessage(message);
      chatInput.value = '';
      
      // If this is a request to generate a cover letter
      if (message.toLowerCase().includes('generate') || 
          message.toLowerCase().includes('create') || 
          message.toLowerCase().includes('cover letter')) {
        generateCoverLetter();
      } else {
        // Handle regular chat message (for refining cover letter, etc.)
        simulateBotResponse(message);
      }
    }
  }
  
  function addUserMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', 'user');
    messageEl.textContent = message;
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  function addBotMessage(message) {
    const messageEl = document.createElement('div');
    messageEl.classList.add('message', 'bot');
    messageEl.textContent = message;
    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
  
  // Just for demo - in real app this would call the API
  function simulateBotResponse(userMessage) {
    // Show typing indicator
    const loadingMessage = "Thinking...";
    const loadingEl = document.createElement('div');
    loadingEl.classList.add('message', 'bot');
    loadingEl.textContent = loadingMessage;
    chatMessages.appendChild(loadingEl);
    
    setTimeout(() => {
      // Replace loading message with actual response
      chatMessages.removeChild(loadingEl);
      
      let response;
      if (userMessage.toLowerCase().includes('thank')) {
        response = "You're welcome! Is there anything else I can help you with?";
      } else if (userMessage.toLowerCase().includes('experience')) {
        response = "I can help emphasize your experience. Would you like to highlight specific skills or achievements?";
      } else if (userMessage.toLowerCase().includes('skills')) {
        response = "Great! I'll make sure to highlight your technical skills more prominently in the letter.";
      } else {
        response = "I've noted your feedback. Would you like me to regenerate the cover letter with these changes?";
      }
      
      addBotMessage(response);
    }, 1000);
  }
  
  // Generate a sample cover letter - in real app this would call the API
  async function generateCoverLetter() {
    // Show typing indicator
    const loadingMessage = "Generating your cover letter...";
    const loadingEl = document.createElement('div');
    loadingEl.classList.add('message', 'bot');
    loadingEl.textContent = loadingMessage;
    chatMessages.appendChild(loadingEl);
    
    try {
      // Get selected jobs
      const selectedJobs = jobs.filter(job => job.selected);
      
      // Call API to generate cover letter
      const response = await coverLettersApi.generateCoverLetter(userProfile.id, selectedJobs[0].id);
      
      // Replace loading message with generated letter
      chatMessages.removeChild(loadingEl);
      
      // Add the letter to chat
      addBotMessage(`Here's your generated cover letter for ${selectedJobs[0].company}:`);
      addBotMessage(response.cover_letter_text);
      
      // Make current letter active
      currentLetter = {
        text: response.cover_letter_text,
        job: selectedJobs[0],
        date: new Date()
      };
      
      saveLetterBtn.disabled = false;
    } catch (error) {
      // Replace loading message with error
      chatMessages.removeChild(loadingEl);
      addBotMessage(`Error generating cover letter: ${error.message}`);
    }
  }
  
  // Save letter functionality
  saveLetterBtn.addEventListener('click', () => {
    if (currentLetter) {
      savedLetters.push(currentLetter);
      saveLetterBtn.disabled = true;
      updateSavedLettersList();
      addBotMessage("Your cover letter has been saved! You can access it anytime in the Saved Letters panel.");
    }
  });
  
  // Job selection functionality
  document.addEventListener('click', async (e) => {
    if (e.target.closest('.select-job')) {
      const button = e.target.closest('.select-job');
      const jobId = parseInt(button.getAttribute('data-job-id'));
      
      // Find the job being clicked
      const job = jobs.find(j => j.id === jobId);
      if (job) {
        // If job is already selected, do nothing (prevent deselection)
        if (job.selected) {
          return;
        }
        
        // Deselect all jobs first
        jobs.forEach(j => {
          if (j.selected) {
            j.selected = false;
            // Find and update the corresponding button icon
            const jobButton = document.querySelector(`.select-job[data-job-id="${j.id}"]`);
            if (jobButton) {
              const jobIcon = jobButton.querySelector('i');
              if (jobIcon) {
                jobIcon.textContent = 'check_box_outline_blank';
              }
            }
          }
        });
        
        // Select the clicked job
        job.selected = true;
        
        // Update icon
        const icon = button.querySelector('i');
        icon.textContent = 'check_box';
        
        // Update selected count
        updateSelectedJobsCount();
      }
    }
    
    if (e.target.closest('.delete-job')) {
      const button = e.target.closest('.delete-job');
      const jobId = parseInt(button.getAttribute('data-job-id'));
      
      // Confirm before deleting
      if (confirm('Are you sure you want to delete this job?')) {
        try {
          // Show a temporary "Deleting..." message
          const jobItem = button.closest('.job-item');
          const originalContent = jobItem.innerHTML;
          jobItem.innerHTML = '<div class="deleting">Deleting job...</div>';
          
          // Call API to delete the job
          await jobsApi.deleteJob(jobId);
          
          // Update local state after successful deletion
          jobs = jobs.filter(j => j.id !== jobId);
          
          // Update UI
          updateJobsList();
          updateSelectedJobsCount();
        } catch (error) {
          // Show error and restore original content
          alert('Error deleting job: ' + error.message);
        }
      }
    }
  });
  
  // Save profile functionality
  saveProfileBtn.addEventListener('click', async () => {
    try {
      const fullName = document.getElementById('full-name').value;
      const nameParts = fullName.split(' ');
      const name = nameParts[0] || '';
      const surname = nameParts.slice(1).join(' ') || '';
      
      const userData = {
        name: name,
        surname: surname,
        email: document.getElementById('email').value,
        cv_text: document.getElementById('resume-text').value
      };
      
      // Update user in database
      if (userProfile.id) {
        await userApi.updateUserProfile(userProfile.id, userData);
      }
      
      // Update local state
      userProfile = {
        ...userProfile,
        fullName: fullName,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        resume: document.getElementById('resume-text').value
      };
      
      profileModal.classList.remove('active');
      addBotMessage(`Thanks ${userProfile.fullName}! Your profile has been updated. Now you can generate a personalized cover letter.`);
    } catch (error) {
      console.error('Error saving profile:', error);
      alert('Error saving profile: ' + error.message);
    }
  });
  
  // Add job functionality
  addJobSubmit.addEventListener('click', async () => {
    // Get active source option to determine which panel to use
    const activeOption = document.querySelector('.source-option.active');
    if (!activeOption) {
      console.error('No active option found');
      return;
    }
    
    const activePanel = activeOption.getAttribute('data-panel');
    console.log(`Active panel: ${activePanel}`); // Debug log
    
    try {
      let newJob;
      
      // Handle different input methods
      if (activePanel === 'url-panel') {
        // URL-based job creation
        const url = document.getElementById('job-url').value;
        if (!url) {
          alert('Please enter a job posting URL');
          return;
        }
        
        // Format data according to API requirements
        const jobData = {
          title: 'Job from URL', // Will be extracted by backend
          company: 'Unknown',     // Will be extracted by backend  
          job_data: `Job URL: ${url}`,
          user_id: userProfile.id || 1 // Use profile ID or default
        };
        
        console.log('Creating job from URL:', url);
        newJob = await jobsApi.createJob(jobData);
        
      } else if (activePanel === 'text-panel') {
        const jobText = document.getElementById('job-text').value;
        
        // Data validation
        if (!jobText) {
          alert('Please fill out all required fields');
          return;
        }
        
        // Prepare data for API
        const jobData = {
          title: '', // Will be extracted by backend
          company: '',     // Will be extracted by backend  
          job_data: jobText,
          user_id: userProfile.id || 1 // Use profile ID or default
        };
        
        console.log('Creating job from text input');
        newJob = await jobsApi.createJob(jobData);
        
      } else if (activePanel === 'file-panel') {
        // File upload job creation
        if (!jobFile.files.length) {
          alert('Please upload a job posting file');
          return;
        }
        
        // FormData is needed for file uploads
        const formData = new FormData();
        formData.append('file', jobFile.files[0]);
        formData.append('user_id', userProfile.id || 1);
        
        console.log('Uploading job file:', jobFile.files[0].name);
        newJob = await jobsApi.uploadJobFile(formData);
      } else if(activePanel === 'manual-panel') {
        // Manual entry job creation
        const title = document.getElementById('job-title').value;
        const company = document.getElementById('job-company').value;
        const description = document.getElementById('job-description').value;

        // Data validation
        if (!title || !company || !description) {
          alert('Please fill out all required fields');
          return;
        }
        
        // Prepare data for API
        const jobData = {
          title: title,
          company: company,
          job_data: description,
          user_id: userProfile.id || 1 // Use profile ID or default
        };
        
        console.log('Creating job from manual input');
        newJob = await jobsApi.createJob(jobData);
      }
      
      // Handle successful creation
      if (newJob) {
        console.log('Job created successfully:', newJob);
        
        // Add the selected property needed by UI
        newJob.selected = false;
        // Handle property differences between API and UI
        newJob.description = newJob.job_data || newJob.description || 'No description available';
        
        // Update our local data
        jobs.push(newJob);
        
        // Update UI
        updateJobsList();
        updateSelectedJobsCount();
        
        // Reset form & close modal
        closeJobModal();
      }
    } catch (error) {
      console.error('Error adding job:', error);
      alert(`Failed to add job: ${error.message || 'Unknown error'}`);
    }
  });
  
  // Helper functions
  function updateJobsList() {
    const jobsContainer = document.querySelector('.jobs-container');
    
    // Clear existing job items (except the empty state)
    const existingJobs = jobsContainer.querySelectorAll('.job-item');
    existingJobs.forEach(job => job.remove());
    
    // Show/hide empty state
    if (jobs.length === 0) {
      emptyJobsState.classList.remove('hidden');
    } else {
      emptyJobsState.classList.add('hidden');
      
      // Add job items
      jobs.forEach(job => {
        const jobItem = document.createElement('div');
        jobItem.classList.add('job-item');
        
        const jobHeader = document.createElement('div');
        jobHeader.classList.add('job-header');
        
        const jobTitle = document.createElement('div');
        jobTitle.classList.add('job-title');
        jobTitle.textContent = `${job.title} at ${job.company || 'Unknown'}`;
        
        const jobActions = document.createElement('div');
        jobActions.classList.add('job-actions');
        
        const selectBtn = document.createElement('button');
        selectBtn.classList.add('select-job');
        selectBtn.setAttribute('data-job-id', job.id);
        selectBtn.innerHTML = `<i class="material-icons">${job.selected ? 'check_box' : 'check_box_outline_blank'}</i>`;
        
        const deleteBtn = document.createElement('button');
        deleteBtn.classList.add('delete-job');
        deleteBtn.setAttribute('data-job-id', job.id);
        deleteBtn.innerHTML = '<i class="material-icons">delete</i>';
        
        jobActions.appendChild(selectBtn);
        jobActions.appendChild(deleteBtn);
        
        jobHeader.appendChild(jobTitle);
        jobHeader.appendChild(jobActions);
        
        const jobDescription = document.createElement('div');
        jobDescription.classList.add('job-description');
        // Use job_data if available, otherwise use description
        const descriptionText = job.job_data || job.description;
        jobDescription.textContent = descriptionText ? 
          (descriptionText.substring(0, 150) + '...') : 
          'No description available';
        
        jobItem.appendChild(jobHeader);
        jobItem.appendChild(jobDescription);
        
        jobsContainer.appendChild(jobItem);
      });
    }
  }
  
  function updateSelectedJobsCount() {
    const selectedCount = jobs.filter(job => job.selected).length;
    const selectedJobsCount = document.getElementById('selected-jobs-count');
    selectedJobsCount.textContent = `${selectedCount} job${selectedCount !== 1 ? 's' : ''} selected`;
  }
  
  function updateSavedLettersList() {
    const savedLettersContainer = document.getElementById('saved-letters');
    
    // Clear existing letters (except the empty state)
    const existingLetters = savedLettersContainer.querySelectorAll('.saved-letter-item');
    existingLetters.forEach(letter => letter.remove());
    
    // Show/hide empty state
    if (savedLetters.length === 0) {
      emptySavedState.classList.remove('hidden');
    } else {
      emptySavedState.classList.add('hidden');
      
      // Add letter items
      savedLetters.forEach((letter, index) => {
        const letterItem = document.createElement('div');
        letterItem.classList.add('saved-letter-item');
        letterItem.setAttribute('data-letter-index', index);
        
        const letterHeader = document.createElement('div');
        letterHeader.classList.add('saved-letter-header');
        
        const letterTitle = document.createElement('div');
        letterTitle.classList.add('saved-letter-title');
        letterTitle.textContent = `Letter for ${letter.job.company}`;
        
        const letterDate = document.createElement('div');
        letterDate.classList.add('saved-letter-date');
        letterDate.textContent = new Date(letter.date).toLocaleDateString();
        
        letterHeader.appendChild(letterTitle);
        letterHeader.appendChild(letterDate);
        
        const letterPreview = document.createElement('div');
        letterPreview.classList.add('saved-letter-preview');
        letterPreview.textContent = letter.text.substring(0, 150) + '...';
        
        letterItem.appendChild(letterHeader);
        letterItem.appendChild(letterPreview);
        
        // Add click handler to load letter
        letterItem.addEventListener('click', () => {
          loadSavedLetter(index);
        });
        
        savedLettersContainer.appendChild(letterItem);
      });
    }
  }
  
  function loadSavedLetter(index) {
    const letter = savedLetters[index];
    if (letter) {
      // Activate chat panel
      document.querySelector('[data-panel="chat"]').click();
      
      // Add the letter to chat
      addBotMessage(`Here's your saved letter for ${letter.job.company}:`);
      addBotMessage(letter.text);
      
      // Make current letter active
      currentLetter = letter;
      saveLetterBtn.disabled = true; // Already saved
    }
  }
  
  async function loadUserProfile() {
    try {
      // Try to load profile from API
      const user = await userApi.getUserProfile(userProfile.id);
      
      if (user) {
        console.log('Loaded user profile:', user);
        userProfile = {
          id: user.id,
          fullName: `${user.name || ''} ${user.surname || ''}`.trim(),
          email: user.email || '',
          phone: '', // Add to your user model if needed
          resume: user.cv_text || ''
        };
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
    
    // Populate form with current profile data
    document.getElementById('full-name').value = userProfile.fullName || '';
    document.getElementById('email').value = userProfile.email || '';
    document.getElementById('phone').value = userProfile.phone || '';
    document.getElementById('resume-text').value = userProfile.resume || '';
  }
  
  // App initialization function - loads data from API
  async function initializeApp() {
    try {
      // Load user profile
      const userProfileData = await userApi.getUserProfile(1); // Default user ID
      if (userProfileData) {
        userProfile = {
          id: userProfileData.id,
          fullName: `${userProfileData.name} ${userProfileData.surname}`,
          email: userProfileData.email,
          phone: userProfileData.phone || '',
          resume: userProfileData.cv_text || ''
        };
        
        // Update profile form with user data
        updateProfileForm();
      }
      
      // Load jobs
      const jobsData = await jobsApi.getAllJobs();
      jobs = jobsData.map(job => ({
        ...job,
        selected: false
      }));
      
      // Update UI
      updateJobsList();
      
    } catch (error) {
      console.error('Error initializing app:', error);
    }
  }
  
  // Update profile form with current user data
  function updateProfileForm() {
    // Get form elements
    const fullNameInput = document.getElementById('full-name');
    const emailInput = document.getElementById('email');
    const phoneInput = document.getElementById('phone');
    const resumeTextarea = document.getElementById('resume-text');
    
    // Set values
    if (fullNameInput) fullNameInput.value = userProfile.fullName;
    if (emailInput) emailInput.value = userProfile.email;
    if (phoneInput) phoneInput.value = userProfile.phone;
    if (resumeTextarea) resumeTextarea.value = userProfile.resume;
  }
  
  // Profile modal functionality
  if (profileBtn) {
    profileBtn.addEventListener('click', () => {
      // Update form with latest user data
      updateProfileForm();
      
      // Show modal
      profileModal.classList.add('active');
    });
  }
  
  if (closeProfileBtn) {
    closeProfileBtn.addEventListener('click', () => {
      profileModal.classList.remove('active');
    });
  }
  
  // Resume file upload handling
  if (resumeFile) {
    resumeFile.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        const file = e.target.files[0];
        resumeFileName.textContent = file.name;
        resumeFileName.style.display = 'block';
        
        // For text-based files, we can read and display the content
        if (file.type === 'text/plain' || file.name.endsWith('.md')) {
          const reader = new FileReader();
          reader.onload = function(e) {
            document.getElementById('resume-text').value = e.target.result;
          };
          reader.readAsText(file);
        }
      }
    });
  }
  
  // Save profile functionality
  if (saveProfileBtn) {
    saveProfileBtn.addEventListener('click', async () => {
      try {
        // Get form values
        const fullName = document.getElementById('full-name').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const resumeText = document.getElementById('resume-text').value;
        
        // Basic validation
        if (!fullName || !email) {
          alert('Please fill out required fields (name and email)');
          return;
        }
        
        // Split full name into first and last name
        const nameParts = fullName.split(' ');
        const firstName = nameParts[0];
        const lastName = nameParts.slice(1).join(' ');
        
        // Prepare data for API
        const userData = {
          name: firstName,
          surname: lastName,
          email: email,
          phone: phone,
          cv_text: resumeText
        };
        
        // Update user profile via API
        const updatedUser = await userApi.updateUserProfile(userProfile.id, userData);
        
        // Update local state
        userProfile = {
          id: updatedUser.id,
          fullName: `${updatedUser.name} ${updatedUser.surname}`,
          email: updatedUser.email,
          phone: updatedUser.phone || '',
          resume: updatedUser.cv_text || ''
        };
        
        // Close modal and show success message
        profileModal.classList.remove('active');
        alert('Profile updated successfully!');
        
      } catch (error) {
        console.error('Error saving profile:', error);
        alert(`Error saving profile: ${error.message}`);
      }
    });
  }
  
  // Initialize the app
  initializeApp();
  
  // Quick Options functionality
  if (generateCoverLetterBtn) {
    generateCoverLetterBtn.addEventListener('click', () => {
      // Check if any jobs are selected
      const selectedJobs = jobs.filter(job => job.selected);
      if (selectedJobs.length === 0) {
        alert('Please select at least one job posting first.');
        return;
      }
      
      // Add a user message indicating the request
      addUserMessage('Generate a cover letter for the selected job');
      
      // Generate the cover letter
      generateCoverLetter();
    });
  }
  
  if (customizeLetterBtn) {
    customizeLetterBtn.addEventListener('click', () => {
      if (!currentLetter) {
        alert('Please generate a cover letter first.');
        return;
      }
      
      addUserMessage('Customize this letter to highlight my experience');
      simulateBotResponse('Customize this letter to highlight my experience');
    });
  }
  
  if (highlightSkillsBtn) {
    highlightSkillsBtn.addEventListener('click', () => {
      if (!currentLetter) {
        alert('Please generate a cover letter first.');
        return;
      }
      
      addUserMessage('Highlight my technical skills more prominently');
      simulateBotResponse('Highlight my technical skills more prominently');
    });
  }
  
  if (formalToneBtn) {
    formalToneBtn.addEventListener('click', () => {
      if (!currentLetter) {
        alert('Please generate a cover letter first.');
        return;
      }
      
      addUserMessage('Make the tone more formal and professional');
      simulateBotResponse('Make the tone more formal and professional');
    });
  }
  
  // Suggested prompts functionality
  suggestedPrompts.forEach(prompt => {
    prompt.addEventListener('click', () => {
      const promptText = prompt.getAttribute('data-prompt');
      
      // Set the prompt text in the input field
      chatInput.value = promptText;
      
      // Focus the input field
      chatInput.focus();
    });
  });
});
