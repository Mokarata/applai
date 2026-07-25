const API_BASE_URL = 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// A helper function to handle API requests and responses
const globalHeaders = {
  'Content-Type': 'application/json',
  'Cache-Control': 'no-cache',
};

const request = async (endpoint, options = {}) => {
  const config = {
    ...options,
    headers: { ...globalHeaders, ...options.headers },
  };

  // For FormData, let the browser set the Content-Type header automatically
  if (config.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(errorData.detail || `HTTP error! status: ${response.status}`, response.status);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
};

// --- Auth API --- //
export const logout = () => {
  localStorage.removeItem('accessToken');
  delete globalHeaders['Authorization'];
};

export const login = async (username, password) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const data = await request('/auth/token', {
    method: 'POST',
    body: formData,
  });

  if (data.access_token) {
    localStorage.setItem('accessToken', data.access_token);
    setAuthHeader(data.access_token);
  }
  return data;
};

export const setAuthHeader = (token) => {
  if (token) {
    globalHeaders['Authorization'] = `Bearer ${token}`;
  } else {
    delete globalHeaders['Authorization'];
  }
};



// --- User Profile API --- //
export const getUserProfile = (userId) => request(`/users/${userId}`);

export const getCurrentUserProfile = () => request('/users/me');

export const updateUserProfile = async (userId, profileData) => {
  return await request(`/users/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(profileData),
  });
};

// --- Jobs API --- //
export const getJobs = async (userId) => {
  return await request(`/jobs/?user_id=${userId}`);
};

export const addJob = async (formData) => {
  // The body is now FormData, and the 'request' helper will handle headers.
  return await request('/jobs/', {
    method: 'POST',
    body: formData,
  });
};

export const deleteJob = async (jobId) => {
  return await request(`/jobs/${jobId}`, { method: 'DELETE' });
};

export const deleteJobs = async (jobIds) => {
  return await request('/jobs/', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_ids: jobIds }),
  });
};



// --- Cover Letter API --- //
export const generateCoverLetter = async (jobId, options, signal) => {
  // Calls the new generation endpoint.
  const endpoint = `/cover-letters/generate?job_id=${jobId}`;
  return await request(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      generation_options: options
    }),
  });
};

export const saveCoverLetter = async (letterData) => {
  // Calls the new save endpoint.
  return await request('/cover-letters/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(letterData),
  });
};

export const getCoverLetters = async (userId) => {
    return await request(`/cover-letters/?user_id=${userId}`);
};

export const deleteCoverLetter = async (coverLetterId) => {
    return await request(`/cover-letters/${coverLetterId}`, { method: 'DELETE' });
};

export const deleteCoverLetters = async (coverLetterIds) => {
  return await request('/cover-letters/', {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ cover_letter_ids: coverLetterIds }),
  });
};

// --- Chat API --- //
export const sendChatMessage = async (sessionId, userMessage, aiMessage = null, signal) => {
    const payload = {
        session_id: sessionId,
        user_message: userMessage,
        ai_message: aiMessage, // Pass the last AI message for context
    };

    return await request('/chat/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal, // Pass the signal to the fetch request
    });
};
