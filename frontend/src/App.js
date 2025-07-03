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

const USER_ID = 1; // Hardcoded for now

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


  useEffect(() => {
    // Check for a token in localStorage on initial load
    const token = localStorage.getItem('accessToken');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []); // Run only once on component mount

  useEffect(() => {
    const loadData = async () => {
      if (!isAuthenticated) return; // Don't load data if not authenticated

      try {
        const [userData, jobsData, coverLettersData] = await Promise.all([
          api.getUserProfile(USER_ID),
          api.getJobs(USER_ID),
          api.getCoverLetters(USER_ID)
        ]);

        setUser(userData);
        setJobs(jobsData);
        setCoverLetters(coverLettersData);
      } catch (error) {
        console.error('Failed to load initial data:', error);
        if (error.name === 'ApiError' && error.status === 401) {
          // Token is likely expired or invalid, force logout
          handleLogout();
        }
      }
    };

    loadData();
  }, [isAuthenticated]); // This effect runs when isAuthenticated changes

  useEffect(() => {
    const managePolling = () => {
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
            const latestJobs = await api.getJobs(USER_ID);
            
            setJobs(currentJobs => {
              let wasChanged = false;
              const updatedJobs = currentJobs.map(job => {
                if (job.status !== 'processing') {
                  return job;
                }
                const latestVersion = latestJobs.find(j => j.id === job.id);
                if (latestVersion && latestVersion.extracted_data) {
                  console.log(`Job ${latestVersion.id} has been updated.`);
                  wasChanged = true;
                  return { ...latestVersion, status: 'completed' };
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
        pollingRef.current = null;
      }
    };
  }, [jobs, USER_ID]);

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
    try {
      const coverLettersData = await api.getCoverLetters(USER_ID);
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
    try {
      const nameParts = profileData.full_name.split(' ');
      const firstName = nameParts[0];
      const lastName = nameParts.slice(1).join(' ');

      const updatedUser = await api.updateUserProfile(USER_ID, {
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

      {isAddJobModalOpen && <AddJobModal onClose={() => setAddJobModalOpen(false)} onJobAdded={handleJobAdded} userId={USER_ID} />}
      {isProfileModalOpen && <UserProfileModal user={user} onClose={() => setProfileModalOpen(false)} onSave={handleProfileSave} />}
    </div>
  );
}

export default App;
