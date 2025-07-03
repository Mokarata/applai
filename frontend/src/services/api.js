const API_BASE_URL = 'http://localhost:8000/api';

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

// A helper function to handle API requests and responses
let accessToken = localStorage.getItem('accessToken');

const request = async (endpoint, options = {}) => {
  const headers = {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0',
    ...options.headers,
  };

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  // For FormData, let the browser set the Content-Type
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const config = {
    ...options,
    headers,

  };
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, config);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); // Gracefully handle non-JSON error responses
    throw new ApiError(errorData.detail || `HTTP error! status: ${response.status}`, response.status);
  }
  // For 204 No Content responses
  if (response.status === 204) {
    return null;
  }
  return response.json();
};

// --- Auth API --- //
export const logout = () => {
  accessToken = null;
  localStorage.removeItem('accessToken');
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
    accessToken = data.access_token;
    localStorage.setItem('accessToken', accessToken);
  }
  return data;
};

// --- User Profile API --- //
export const getUserProfile = async (userId) => {
  return await request(`/users/${userId}`);
};

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
export const generateCoverLetter = async (jobId, options) => {
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
export const generateResponse = async (userId, jobId, message) => {
    const endpoint = `/chat/?user_id=${userId}&job_id=${jobId}`;
    return await request(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message }),
    });
};
