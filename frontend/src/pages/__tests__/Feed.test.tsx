import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Feed from '../Feed';
import * as api from '../../services/api';
import type { Article } from '../../types';

// Mock the API module
jest.mock('../../services/api');
const mockApi = api as jest.Mocked<typeof api>;

const mockArticles: Article[] = [
  {
    id: '1',
    title: 'Aviation News Article 1',
    body: 'This is the body of aviation news article 1',
    date: '2024-01-15T10:00:00Z',
    link: 'https://example.com/article1',
    source: 'Aviation Week',
    status: 'new',
  },
  {
    id: '2',
    title: 'Airline Industry Update',
    body: 'Latest updates from the airline industry',
    date: '2024-01-16T11:00:00Z',
    link: 'https://example.com/article2',
    source: 'Flight Global',
    status: 'selected',
  },
  {
    id: '3',
    title: 'Aircraft Technology News',
    body: 'New developments in aircraft technology',
    date: '2024-01-17T12:00:00Z',
    link: 'https://example.com/article3',
    source: 'AIN Online',
    status: 'edited',
  },
];

const renderFeed = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <Feed />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Feed Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    mockApi.getNews.mockResolvedValue(mockArticles);
  });

  describe('Rendering', () => {
    it('renders feed header with title and actions', async () => {
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('News Feed')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /update news/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /export/i })).toBeInTheDocument();
      });
    });

    it('renders filter controls', async () => {
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByPlaceholderText(/search articles/i)).toBeInTheDocument();
        expect(screen.getByDisplayValue(/all status/i)).toBeInTheDocument();
        expect(screen.getByDisplayValue(/all sources/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /show advanced/i })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /show presets/i })).toBeInTheDocument();
      });
    });

    it('renders articles after loading', async () => {
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
        expect(screen.getByText('Airline Industry Update')).toBeInTheDocument();
        expect(screen.getByText('Aircraft Technology News')).toBeInTheDocument();
      });
    });

    it('shows loading state initially', () => {
      renderFeed();
      
      expect(screen.getByText(/loading news feed/i)).toBeInTheDocument();
    });
  });

  describe('Search Functionality', () => {
    it('filters articles by search term', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'aviation');
      
      expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      expect(screen.queryByText('Airline Industry Update')).not.toBeInTheDocument();
      expect(screen.queryByText('Aircraft Technology News')).not.toBeInTheDocument();
    });

    it('searches in title, body, and source', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'technology');
      
      expect(screen.getByText('Aircraft Technology News')).toBeInTheDocument();
      expect(screen.queryByText('Aviation News Article 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Airline Industry Update')).not.toBeInTheDocument();
    });

    it('shows no results message when no matches', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'nonexistent');
      
      expect(screen.getByText(/no articles found matching your filters/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear filters/i })).toBeInTheDocument();
    });
  });

  describe('Status Filtering', () => {
    it('filters articles by status', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const statusSelect = screen.getByDisplayValue(/all status/i);
      await user.selectOptions(statusSelect, 'selected');
      
      expect(screen.getByText('Airline Industry Update')).toBeInTheDocument();
      expect(screen.queryByText('Aviation News Article 1')).not.toBeInTheDocument();
      expect(screen.queryByText('Aircraft Technology News')).not.toBeInTheDocument();
    });
  });

  describe('Source Filtering', () => {
    it('filters articles by source', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const sourceSelect = screen.getByDisplayValue(/all sources/i);
      await user.selectOptions(sourceSelect, 'Aviation Week');
      
      expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      expect(screen.queryByText('Airline Industry Update')).not.toBeInTheDocument();
      expect(screen.queryByText('Aircraft Technology News')).not.toBeInTheDocument();
    });
  });

  describe('Advanced Filters', () => {
    it('shows advanced filters when toggle is clicked', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const advancedButton = screen.getByRole('button', { name: /show advanced/i });
      await user.click(advancedButton);
      
      expect(screen.getByText(/from date/i)).toBeInTheDocument();
      expect(screen.getByText(/to date/i)).toBeInTheDocument();
      expect(screen.getByText(/search in/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /clear all filters/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save as preset/i })).toBeInTheDocument();
    });

    it('filters by date range', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      // Show advanced filters
      await user.click(screen.getByRole('button', { name: /show advanced/i }));
      
      const fromDateInput = screen.getByLabelText(/from date/i);
      const toDateInput = screen.getByLabelText(/to date/i);
      
      await user.type(fromDateInput, '2024-01-16');
      await user.type(toDateInput, '2024-01-17');
      
      // Only "Airline Industry Update" (Jan 16) should be visible for this date range
      expect(screen.getByText('Airline Industry Update')).toBeInTheDocument();
      expect(screen.queryByText('Aircraft Technology News')).not.toBeInTheDocument();
      expect(screen.queryByText('Aviation News Article 1')).not.toBeInTheDocument();
    });

    it('filters by advanced search options', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      // Show advanced filters
      await user.click(screen.getByRole('button', { name: /show advanced/i }));
      
      // Check title only
      const titleOnlyCheckbox = screen.getByLabelText(/title only/i);
      await user.click(titleOnlyCheckbox);
      
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'aviation');
      
      expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      expect(screen.queryByText('Airline Industry Update')).not.toBeInTheDocument();
    });
  });

  describe('Filter Presets', () => {
    it('shows presets when toggle is clicked', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const presetsButton = screen.getByRole('button', { name: /show presets/i });
      await user.click(presetsButton);
      
      expect(screen.getByText(/saved filter presets/i)).toBeInTheDocument();
      expect(screen.getByText(/no saved presets/i)).toBeInTheDocument();
    });

    it('saves current filter as preset', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      // Show advanced filters
      await user.click(screen.getByRole('button', { name: /show advanced/i }));
      
      // Set some filters
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'aviation');
      
      // Mock prompt BEFORE clicking the button
      const mockPrompt = jest.spyOn(window, 'prompt').mockReturnValue('My Preset');
      
      const savePresetButton = screen.getByRole('button', { name: /save as preset/i });
      await user.click(savePresetButton);
      
      expect(mockPrompt).toHaveBeenCalledWith('Enter a name for this filter preset:');
      expect(screen.getByText(/filter preset "my preset" saved successfully/i)).toBeInTheDocument();
      
      mockPrompt.mockRestore();
    });
  });

  describe('Export Functionality', () => {
    it('exports filtered articles', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const exportButton = screen.getByRole('button', { name: /export/i });
      await user.click(exportButton);
      
      expect(screen.getByText(/articles exported successfully/i)).toBeInTheDocument();
    });

    it('disables export when no articles', async () => {
      mockApi.getNews.mockResolvedValue([]);
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /export/i })).toBeDisabled();
      });
    });
  });

  describe('Clear Filters', () => {
    it('clears all filters when clear button is clicked', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      // Set some filters
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'aviation');
      
      expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      expect(screen.queryByText('Airline Industry Update')).not.toBeInTheDocument();
      
      // Clear filters
      const clearButton = screen.getByRole('button', { name: /clear filters/i });
      await user.click(clearButton);
      
      expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      expect(screen.getByText('Airline Industry Update')).toBeInTheDocument();
      expect(screen.getByText('Aircraft Technology News')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles API errors gracefully', async () => {
      mockApi.getNews.mockRejectedValue(new Error('API Error'));
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText(/could not load news/i)).toBeInTheDocument();
      });
    });

    it('handles network connection errors', async () => {
      mockApi.getNews.mockRejectedValue(new Error('Failed to fetch'));
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText(/could not connect to the backend/i)).toBeInTheDocument();
      });
    });
  });

  describe('Results Information', () => {
    it('shows correct results count', async () => {
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText(/showing 3 of 3 articles/i)).toBeInTheDocument();
      });
    });

    it('shows filtered results count', async () => {
      const user = userEvent.setup();
      renderFeed();
      
      await waitFor(() => {
        expect(screen.getByText('Aviation News Article 1')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText(/search articles/i);
      await user.type(searchInput, 'aviation');
      
      expect(screen.getByText(/showing 1 of 3 articles/i)).toBeInTheDocument();
    });
  });
}); 