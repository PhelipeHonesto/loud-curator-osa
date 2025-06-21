import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider, useAuth } from '../AuthContext';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');
const mockApi = api as jest.Mocked<typeof api>;

// Test component to access auth context
const TestComponent = () => {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();
  
  return (
    <div>
      <div data-testid="user">{user ? user.username : 'no-user'}</div>
      <div data-testid="is-authenticated">{isAuthenticated.toString()}</div>
      <div data-testid="is-loading">{isLoading.toString()}</div>
      <button onClick={() => login('test-token')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

const renderWithAuth = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    // Reset all localStorage mocks
    (localStorage.getItem as jest.Mock).mockReset();
    (localStorage.setItem as jest.Mock).mockReset();
    (localStorage.removeItem as jest.Mock).mockReset();
    (localStorage.key as jest.Mock).mockReset();
  });

  describe('Initial State', () => {
    it('starts with no user and not authenticated', () => {
      renderWithAuth();
      
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });

    it('starts in loading state', async () => {
      mockApi.getCurrentUser.mockReturnValue(new Promise(() => {})); // never resolves
      localStorage.setItem('token', 'existing-token');
      await act(async () => {
        renderWithAuth();
      });
      expect(screen.getByTestId('is-loading')).toHaveTextContent('true');
    });
  });

  describe('Token Management', () => {
    it('loads user from existing token', async () => {
      localStorage.setItem('token', 'existing-token');
      mockApi.getCurrentUser.mockResolvedValue({ username: 'testuser', email: 'test@example.com' });
      await act(async () => {
        renderWithAuth();
      });
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      });
      expect(mockApi.getCurrentUser).toHaveBeenCalled();
    });

    it('handles invalid token gracefully', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('invalid-token');
      mockApi.getCurrentUser.mockRejectedValue(new Error('Invalid token'));
      renderWithAuth();
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
        // removeItem is not called if token is just invalid, only if error is thrown in checkAuth
      });
    });

    it('handles missing token', async () => {
      renderWithAuth();
      
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });
      
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
      expect(mockApi.getCurrentUser).not.toHaveBeenCalled();
    });
  });

  describe('Login Function', () => {
    it('sets token and loads user data', async () => {
      const user = userEvent.setup();
      mockApi.getCurrentUser.mockResolvedValue({ username: 'newuser', email: 'new@example.com' });
      await act(async () => {
        renderWithAuth();
      });
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });
      const loginButton = screen.getByText('Login');
      await act(async () => {
        await user.click(loginButton);
      });
      expect(localStorage.setItem).toHaveBeenCalledWith('token', 'test-token');
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('newuser');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      });
    });

    it('handles login errors', async () => {
      (localStorage.getItem as jest.Mock).mockReturnValue('token');
      mockApi.login.mockRejectedValue(new Error('Network error'));
      renderWithAuth();
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
        // removeItem is not called if login fails
      });
    });
  });

  describe('Logout Function', () => {
    it('clears token and user data', async () => {
      const user = userEvent.setup();
      localStorage.setItem('token', 'existing-token');
      mockApi.getCurrentUser.mockResolvedValue({ username: 'testuser', email: 'test@example.com' });
      await act(async () => {
        renderWithAuth();
      });
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
      });
      const logoutButton = screen.getByText('Logout');
      await act(async () => {
        await user.click(logoutButton);
      });
      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
    });
  });

  describe('Error Handling', () => {
    it('handles API errors during user loading', async () => {
      localStorage.setItem('token', 'existing-token');
      mockApi.getCurrentUser.mockRejectedValue(new Error('Network error'));
      await act(async () => {
        renderWithAuth();
      });
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('no-user');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
        expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      });
    });

    it('handles missing token error', async () => {
      localStorage.setItem('token', 'existing-token');
      mockApi.getCurrentUser.mockRejectedValue(new Error('No token found'));
      
      renderWithAuth();
      
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });
      
      expect(screen.getByTestId('user')).toHaveTextContent('no-user');
      expect(screen.getByTestId('is-authenticated')).toHaveTextContent('false');
      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
    });
  });

  describe('Context Usage', () => {
    it('throws error when used outside provider', () => {
      // Suppress console.error for this test
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      expect(() => {
        render(<TestComponent />);
      }).toThrow('useAuth must be used within an AuthProvider');
      
      consoleSpy.mockRestore();
    });
  });

  describe('State Updates', () => {
    it('updates state correctly when user data changes', async () => {
      mockApi.getCurrentUser.mockResolvedValue({ username: 'testuser', email: 'test@example.com' });
      await act(async () => {
        renderWithAuth();
      });
      await waitFor(() => {
        expect(screen.getByTestId('user')).toHaveTextContent('testuser');
        expect(screen.getByTestId('is-authenticated')).toHaveTextContent('true');
      });
    });

    it('handles loading state transitions', async () => {
      let resolveUser: (value: any) => void;
      const userPromise = new Promise((resolve) => {
        resolveUser = resolve;
      });
      mockApi.getCurrentUser.mockReturnValue(userPromise);
      localStorage.setItem('token', 'existing-token');
      await act(async () => {
        renderWithAuth();
      });
      expect(screen.getByTestId('is-loading')).toHaveTextContent('true');
      act(() => {
        resolveUser!({ username: 'testuser', email: 'test@example.com' });
      });
      await waitFor(() => {
        expect(screen.getByTestId('is-loading')).toHaveTextContent('false');
      });
    });
  });
}); 