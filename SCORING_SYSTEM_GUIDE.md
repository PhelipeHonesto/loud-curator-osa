# 🎯 Loud Curator Article Scoring System Guide

## Overview

The Article Scoring System is an intelligent content curation tool that automatically evaluates articles based on three key dimensions and provides distribution recommendations for the Loud Hawk platform.

## 🚀 Quick Start

### 1. Accessing the Scoring System
- Navigate to any article in the Feed
- Click the **"🎯 Score Article"** button on the article card
- The scoring modal will open with the article details and scoring interface

### 2. Understanding the Scores

#### 📊 Relevance Score (0-100)
- **What it measures**: How important the article is for the aviation community
- **High scores (80-100)**: Critical aviation news, safety incidents, major industry developments
- **Medium scores (60-79)**: General aviation updates, airline news, regulatory changes
- **Low scores (0-59)**: Tangentially related content, non-aviation topics

#### 🔥 Vibe Score (0-100)
- **What it measures**: How well the article matches Loud Hawk's rebellious, bold tone
- **High scores (80-100)**: Controversial topics, industry criticism, bold claims
- **Medium scores (60-79)**: Balanced reporting with some edge
- **Low scores (0-59)**: Conservative, corporate, or overly formal content

#### 🚀 Viral Score (0-100)
- **What it measures**: Potential for the article to be shared and go viral
- **High scores (80-100)**: Shocking news, human interest stories, controversy
- **Medium scores (60-79)**: Interesting developments, moderate engagement potential
- **Low scores (0-59)**: Routine updates, technical content, low engagement

## 🎛️ Using the Scoring Interface

### Auto-Scoring
1. Click **"🤖 Auto-Score"** to use AI-powered scoring
2. The system will analyze the article content and generate scores
3. Review the suggested scores and distribution recommendations

### Manual Scoring
1. Use the sliders to adjust scores manually
2. Each slider ranges from 0-100 with color-coded feedback
3. Scores update in real-time with descriptive labels:
   - **🔥 EXCELLENT** (90-100)
   - **⚡ GREAT** (80-89)
   - **✅ GOOD** (70-79)
   - **🟡 DECENT** (60-69)
   - **🟠 WEAK** (40-59)
   - **❌ POOR** (0-39)

### Saving Scores
1. Click **"💾 Save Scores"** to persist your changes
2. Scores are immediately updated in the database
3. The article card will reflect the new scores

## 📡 Distribution Recommendations

### Target Channels
The system recommends which channels to post the article to:

- **💬 Slack**: General aviation community discussions
- **🎨 Figma**: Visual content and design-focused posts
- **📱 WhatsApp**: Quick updates and breaking news
- **👁️ Manual Review**: Content requiring human oversight

### Auto-Post Settings
- **✅ Enabled**: Article will be automatically posted to recommended channels
- **❌ Disabled**: Article requires manual review before posting

### Priority Levels
- **🔴 HIGH**: Urgent content requiring immediate attention
- **🟡 MEDIUM**: Standard content for regular distribution
- **⚫ LOW**: Background content or low-priority updates

## 🎯 Best Practices

### For High-Impact Content
1. **Relevance**: Focus on safety incidents, major accidents, or regulatory changes
2. **Vibe**: Look for controversial angles, industry criticism, or bold statements
3. **Viral**: Prioritize human interest stories, shocking revelations, or industry drama

### Scoring Guidelines
- **Aviation Accidents**: High relevance (90+), high viral (80+), moderate vibe (60-80)
- **Safety Violations**: High relevance (85+), high vibe (80+), high viral (75+)
- **Industry Criticism**: Moderate relevance (70+), high vibe (90+), moderate viral (70+)
- **Technical Updates**: High relevance (80+), low vibe (30-50), low viral (40-60)

### Distribution Strategy
- **Breaking News**: Enable auto-post, target all channels, set high priority
- **Analysis Pieces**: Manual review, target Slack/Figma, medium priority
- **Background Info**: Manual review, target specific channels, low priority

## 🔧 Technical Details

### Score Calculation
The AI scoring engine analyzes:
- Article title and content
- Source credibility and tone
- Current aviation industry context
- Historical engagement patterns

### Distribution Logic
Distribution recommendations are based on:
- Combined score thresholds
- Content type and source
- Current channel performance
- Manual override settings

### Data Persistence
- Scores are stored in the database with timestamps
- Distribution settings are saved per article
- Historical scoring data is maintained for analysis

## 🚨 Troubleshooting

### Common Issues

**Scores not updating**
- Check your internet connection
- Ensure the backend server is running
- Try refreshing the page

**Auto-scoring not working**
- Verify OpenAI API key is configured
- Check backend logs for API errors
- Ensure article has sufficient content

**Distribution not showing**
- Wait for scoring to complete
- Check if article has been scored
- Verify database connection

### Getting Help
- Check the backend logs for detailed error messages
- Verify all environment variables are set correctly
- Test the health endpoint: `GET /health`

## 📈 Advanced Features

### Batch Scoring
- Multiple articles can be scored simultaneously
- Use the auto-scoring feature for efficiency
- Review and adjust scores as needed

### Score Analytics
- Track scoring trends over time
- Identify high-performing content types
- Optimize distribution strategies

### Custom Scoring Rules
- Adjust scoring thresholds based on your needs
- Modify distribution logic for specific channels
- Create custom scoring criteria

## 🎯 Success Metrics

### Key Performance Indicators
- **Scoring Accuracy**: How well scores predict engagement
- **Distribution Efficiency**: Time saved through auto-posting
- **Content Quality**: Improvement in curated content relevance

### Optimization Tips
- Regularly review and adjust scoring criteria
- Monitor distribution channel performance
- Update scoring rules based on audience feedback

---

*For technical support or feature requests, please refer to the project documentation or create an issue in the repository.* 