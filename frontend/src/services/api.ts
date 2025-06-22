import type { Article } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({})); // Catch if the error body is not JSON
    const errorMessage = errorData.detail || `HTTP error! status: ${response.status}`;
    throw new Error(errorMessage);
  }
  return response.json();
};

// Authentication functions
export const login = async (username: string, password: string, isRegister: boolean = false) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const endpoint = isRegister ? '/auth/register' : '/auth/token';
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw { response: { data: errorData } };
  }

  return response.json();
};

export const register = async (username: string, password: string) => {
  return login(username, password, true);
};

export const getCurrentUser = async () => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  return handleResponse(response);
};

// Add authorization header to requests
const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

export const getNews = async (): Promise<Article[]> => {
  const response = await fetch(`${API_BASE_URL}/news`, {
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const ingestNews = async () => {
  const response = await fetch(`${API_BASE_URL}/ingest`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const selectStory = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/select/${storyId}`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const editStory = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/edit/${storyId}`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const postToSlack = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/slack/${storyId}`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const postToSlackFigma = async (storyId: string) => {
  const response = await fetch(`${API_BASE_URL}/slack-figma/${storyId}`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

// Headline remix functions
export const remixHeadline = async (articleId: string) => {
  const response = await fetch(`${API_BASE_URL}/headline/remix/${articleId}`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const saveCustomTitle = async (articleId: string, customTitle: string) => {
  const response = await fetch(`${API_BASE_URL}/headline/save/${articleId}`, { 
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ custom_title: customTitle }),
  });
  return handleResponse(response);
};

export const analyzeHeadline = async (articleId: string) => {
  const response = await fetch(`${API_BASE_URL}/headline/analyze/${articleId}`, { 
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

// Article scoring functions
export const scoreArticle = async (articleId: string) => {
  const response = await fetch(`${API_BASE_URL}/articles/${articleId}/score`, { 
    method: 'POST',
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};

export const updateArticleScores = async (articleId: string, scores: { score_relevance?: number; score_vibe?: number; score_viral?: number }) => {
  const response = await fetch(`${API_BASE_URL}/articles/${articleId}/scores`, { 
    method: 'PUT',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(scores),
  });
  return handleResponse(response);
};

export const getArticleDistribution = async (articleId: string) => {
  const response = await fetch(`${API_BASE_URL}/articles/${articleId}/distribution`, { 
    headers: getAuthHeaders(),
  });
  return handleResponse(response);
};
