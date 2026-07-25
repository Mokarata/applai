import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import SavedLettersPanel from './components/SavedLettersPanel';
import AddJobModal from './modals/AddJobModal';
import UserProfileModal from './modals/UserProfileModal';
import LoginModal from './modals/LoginModal';
import * as api from './services/api';
import './assets/css/main.css';

function App() {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [coverLetters, setCoverLetters] = useState([]);
  const pollingRef = useRef(null);
  const [isAddJobModalOpen, setAddJobModalOpen] = useState(false);
  const [isProfileModalOpen, setProfileModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedJobIds, setSelectedJobIds] = useState(new Set());
  const [selectedCoverLetter, setSelectedCoverLetter] = useState(null);

  // Check for authentication token on initial load
  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      api.setAuthHeader(token); // Set auth header for subsequent requests
      setIsAuthenticated(true);
    }
  }, []);

  // Fetch user profile and data once authenticated
  useEffect(() => {
    const loadInitialData = async () => {
      if (isAuthenticated) {
        try {
          const userData = await api.getCurrentUserProfile();
          setUser(userData);

          const [jobsData, coverLettersData] = await Promise.all([
            api.getJobs(userData.id),
            api.getCoverLetters(userData.id)
          ]);
          setJobs(jobsData);
          setCoverLetters(coverLettersData);
        } catch (error) {          
          console.error('Failed to load user data. Logging out.', error);
          handleLogout(); // If token is invalid, log out
        }
      }
    };
    loadInitialData();
  }, [isAuthenticated]);

  useEffect(() => {
    const managePolling = () => {
      if (!user) return; // Don't poll if there's no user

      const needsPolling = jobs.some(job => job.status === 'processing');

      if (!needsPolling) {
        if (pollingRef.current) {
          console.log("All jobs processed. Stopping polling.");
          clearInterval(pollingRef.current);
          pollingRef.current = null;
        }
        return;
      }

      if (needsPolling && !pollingRef.current) {
        console.log("Starting polling for pending jobs...");
        pollingRef.current = setInterval(async () => {
          try {
            const latestJobs = await api.getJobs(user.id);
            
            setJobs(currentJobs => {
              let wasChanged = false;
              const updatedJobs = currentJobs.map(job => {
                if (job.status !== 'processing') {
                  return job;
                }
                const latestVersion = latestJobs.find(j => j.id === job.id);
                // Revert to checking the status field as the source of truth.
                if (latestVersion && latestVersion.status !== 'processing') {
                  console.log(`Job ${latestVersion.id} has been updated to status: ${latestVersion.status}.`);
                  wasChanged = true;
                  return latestVersion; // Return the complete, updated job object from the server.
                }
                return job;
              });

              if (wasChanged) {
                return updatedJobs;
              }
              return currentJobs;
            });
          } catch (error) {
            console.error("Polling failed, stopping poll.", error);
            if (pollingRef.current) {
              clearInterval(pollingRef.current);
              pollingRef.current = null;
            }
          }
        }, 3000);
      }
    };

    managePolling();

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [jobs, user]);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    setUser(null);
    setJobs([]);
    setCoverLetters([]);
  };

    const handleJobAdded = async (newJob) => {
    try {
      setJobs(prevJobs => [newJob, ...prevJobs]);
      // No need to fetch all jobs again, polling will handle updates.
    } catch (error) {
      console.error('Failed to refresh jobs list', error);
    }
  };

    const handleLetterGenerated = async () => {
    if (!user) return;
    try {
      const coverLettersData = await api.getCoverLetters(user.id);
      setCoverLetters(coverLettersData);
    } catch (error) {
      console.error("Failed to refresh cover letters", error);
    }
  };

  const handleCoverLettersDeleted = async (letterIds) => {
    try {
      await api.deleteCoverLetters(letterIds);
      setCoverLetters(prev => prev.filter(letter => !letterIds.includes(letter.id)));
      if (selectedCoverLetter && letterIds.includes(selectedCoverLetter.id)) {
        setSelectedCoverLetter(null);
      }
    } catch (error) {
      console.error('Failed to delete cover letters:', error);
      alert('Failed to delete cover letters. Please try again.');
    }
  };

  const handleJobsDeleted = async (jobIds) => {
    try {
      await api.deleteJobs(jobIds);
      setJobs(prev => prev.filter(job => !jobIds.includes(job.id)));
      setSelectedJobIds(prev => {
        const newSet = new Set(prev);
        jobIds.forEach(id => newSet.delete(id));
        return newSet;
      });
      if (selectedJob && jobIds.includes(selectedJob.id)) {
        setSelectedJob(null);
      }
    } catch (error) {
      console.error('Failed to delete jobs', error);
    }
  };

  const handleProfileSave = async (profileData) => {
    if (!user) return;
    try {
      const nameParts = profileData.full_name.split(' ');
      const firstName = nameParts[0];
      const lastName = nameParts.slice(1).join(' ');

      const updatedUser = await api.updateUserProfile(user.id, {
        first_name: firstName,
        last_name: lastName,
        email: profileData.email,
        phone_number: profileData.phone,
        resume_text: profileData.resume_text,
      });
      setUser(updatedUser);
      setProfileModalOpen(false);
    } catch (error) {
      console.error('Failed to save profile', error);
    }
  };

  return (
    <div className="app-container">
      {!isAuthenticated && <LoginModal onLoginSuccess={handleLoginSuccess} />}
      <Header user={user} onProfileClick={() => setProfileModalOpen(true)} onLogout={handleLogout} isAuthenticated={isAuthenticated} />
      <div className="panels-container">
        <Sidebar 
          jobs={jobs} 
          onAddJobClick={() => setAddJobModalOpen(true)} 
          onJobSelect={setSelectedJob}
          selectedJob={selectedJob}
          onJobsDeleted={handleJobsDeleted}
          selectedJobIds={selectedJobIds}
          onSelectedJobIdsChange={setSelectedJobIds}
        />
        <main className="panel expanded">
          <ChatContainer 
            user={user} 
            jobs={jobs}
            selectedJob={selectedJob}
            selectedJobIds={selectedJobIds}
            selectedCoverLetter={selectedCoverLetter} 
            onLetterGenerated={handleLetterGenerated} 
          />
        </main>
        <SavedLettersPanel 
          coverLetters={coverLetters} 
          onCoverLetterSelect={setSelectedCoverLetter} 
          selectedCoverLetter={selectedCoverLetter}
          onCoverLettersDeleted={handleCoverLettersDeleted}
        />
      </div>

      {isAddJobModalOpen && <AddJobModal onClose={() => setAddJobModalOpen(false)} onJobAdded={handleJobAdded} userId={user?.id} />}
      {isProfileModalOpen && <UserProfileModal user={user} onClose={() => setProfileModalOpen(false)} onSave={handleProfileSave} />}
    </div>
  );
}

export default App;
