# Loud Curator - AI-Powered News Curation Platform

A comprehensive news curation platform that automatically ingests, processes, and distributes aviation and business news content using AI. Built with FastAPI, React, and integrated with multiple news sources and Slack.

## 🚀 Features

### Core Functionality
- **Multi-Source News Ingestion**: Automatically fetch news from multiple sources
- **AI-Powered Content Processing**: Intelligent article rewriting and summarization
- **Dual-Channel Slack Integration**: Post to regular Slack and Figma-formatted channels
- **Advanced Content Management**: Draft, edit, and publish workflow
- **Real-time Scheduling**: Configurable ingestion and posting schedules

### News Sources
- **Aviation Pages**: Direct aviation industry news
- **NewsData.io**: Comprehensive news API with institutional sources
- **Ground News**: Balanced news coverage with bias detection
- **Institutional Readers**: Reuters, Bloomberg, AP, and other major outlets
- **RSS Feeds**: 10+ aviation and business RSS feeds
- **SkyWest**: Company-specific news and updates

### Content Management
- **Smart Deduplication**: Fuzzy title matching to eliminate duplicates
- **Status Tracking**: New → Selected → Edited → Posted workflow
- **Advanced Filtering**: Search by title, status, source, and date
- **Draft Management**: Save and edit articles before publishing
- **Version Control**: Track article changes and updates

### User Interface
- **Modern React Frontend**: Responsive design with real-time updates
- **Advanced Search & Filter**: Find articles quickly with multiple criteria
- **Article Editor**: Rich editing interface with Slack/Figma previews
- **Settings Management**: Configure API keys and connections via UI
- **Statistics Dashboard**: View article counts and source distribution

### Technical Features
- **SQLite Database**: Scalable data storage with automatic migration
- **Comprehensive Logging**: Structured JSON logging with request tracking
- **Error Handling**: Robust error management and user feedback
- **API Health Monitoring**: Health checks and performance metrics
- **Background Processing**: Asynchronous news ingestion and processing

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLite**: Lightweight, scalable database
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server
- **Pytest**: Comprehensive testing framework

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **CSS3**: Modern styling with animations

### External Integrations
- **OpenAI API**: AI content generation and rewriting
- **Slack Webhooks**: Dual-channel posting
- **NewsData.io API**: Institutional news sources
- **Ground News API**: Balanced news coverage
- **RSS Feed Parsing**: Multiple feed sources

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd loud-curator-osa

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create or migrate the SQLite database
python -c "from database_sqlite import init_database; init_database()"

# Frontend setup
cd ../frontend
npm install

# Start development servers
cd ..
./start_dev.sh
```

### Environment Variables
Create a `.env` file in the backend directory:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
NEWSDATA_API_KEY=your_newsdata_api_key
GROUNDNEWS_API_KEY=your_groundnews_api_key

# Slack Integration
SLACK_WEBHOOK_URL=your_slack_webhook_url
SLACK_WEBHOOK_FIGMA_URL=your_figma_slack_webhook_url

# Database
DATABASE_URL=sqlite:///./news.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
```

## 🎯 Usage

### 1. Initial Setup
1. Configure your API keys in the Settings page
2. Test connections to ensure all services are working
3. Set up your Slack webhooks for posting

### 2. News Ingestion
- **Manual**: Click "Ingest News" to fetch articles immediately
- **Automatic**: Configure scheduler for regular ingestion
- **Sources**: All sources are automatically included

### 3. Content Workflow
1. **Browse**: View all ingested articles in the Feed
2. **Select**: Choose articles for editing
3. **Edit**: Use AI to rewrite or manually edit content
4. **Preview**: See how content will appear in Slack/Figma
5. **Publish**: Post to Slack channels

### 4. Content Management
- **Drafts**: Save articles for later editing
- **Saved**: View published and posted articles
- **Filtering**: Search and filter by various criteria
- **Statistics**: Monitor article counts and sources

## 🔧 Configuration

### Scheduler Settings
Configure automatic news ingestion and posting:

```python
# Example scheduler configuration
scheduler.add_job("ingest_news", "0 */4 * * *")  # Every 4 hours
scheduler.add_job("post_articles", "0 9 * * *")  # Daily at 9 AM
```

### RSS Feed Configuration
Add or modify RSS feeds in `agents/rss_agent.py`:

```python
RSS_FEEDS = [
    "https://aviationweek.com/rss.xml",
    "https://flightglobal.com/rss",
    # Add your custom feeds here
]
```

### Slack Integration
Set up dual-channel posting:
- **Regular Channel**: Standard article posting
- **Figma Channel**: Formatted for design team consumption

See `DUAL_CHANNEL_SETUP.md` for detailed setup instructions.

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=.
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: FastAPI endpoint testing
- **Mock Testing**: Isolated testing with mocked dependencies

## 📊 Monitoring

### Health Checks
- **API Health**: `/health` endpoint for load balancer checks
- **Database Status**: Connection and performance monitoring
- **Scheduler Status**: Job execution monitoring

### Logging
- **Structured Logs**: JSON-formatted logging
- **Request Tracking**: API call monitoring
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Response time tracking

### Statistics
- **Article Counts**: Total articles by status and source
- **API Usage**: External API call statistics
- **Performance Metrics**: Response times and throughput

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment
- **AWS**: ECS, Lambda, or EC2 deployment
- **Google Cloud**: Cloud Run or GKE
- **Azure**: Container Instances or AKS

See `DEPLOYMENT.md` for detailed deployment instructions.

## 🔒 Security

### API Key Management
- Environment variable storage
- UI-based key management
- Connection testing
- Secure transmission

### Data Protection
- SQLite database encryption (optional)
- Secure API endpoints
- CORS configuration
- Input validation

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **Python**: PEP 8 compliance
- **TypeScript**: Strict type checking
- **Testing**: Minimum 80% coverage
- **Documentation**: Comprehensive docstrings

See `CONTRIBUTING.md` for detailed guidelines.

## 📈 Roadmap

### Planned Features
- **User Authentication**: Multi-user support with roles
- **Advanced Analytics**: Content performance tracking
- **Content Scheduling**: Advanced posting schedules
- **API Rate Limiting**: Improved external API management
- **Mobile App**: React Native mobile application

### Performance Improvements
- **Database Optimization**: Query optimization and indexing
- **Caching**: Redis-based caching layer
- **CDN Integration**: Static asset delivery
- **Load Balancing**: Horizontal scaling support

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API keys in Settings
   - Test connections using the UI
   - Check network connectivity

2. **Database Issues**
   - Check file permissions for `news.db`
   - Verify SQLite installation
   - Review migration logs

3. **Scheduler Problems**
   - Check scheduler status at `/scheduler/status`
   - Review application logs
   - Verify cron job syntax

### Getting Help
1. Check the logs in the `logs/` directory
2. Review the troubleshooting section in `DEPLOYMENT.md`
3. Open an issue on GitHub with detailed error information
4. Include system information and deployment environment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI**: For AI content generation capabilities
- **NewsData.io**: For comprehensive news API
- **Ground News**: For balanced news coverage
- **FastAPI**: For the excellent web framework
- **React**: For the powerful frontend framework

## 📞 Support

For support and questions:
- **Documentation**: Check the docs in this repository
- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact the maintainers directly

---

**Loud Curator** - Making news curation intelligent and efficient.
