# Dual-Channel Slack Posting System

## Overview

The Loud Curator now supports **two different Slack channels** for posting curated news:

1. **Default Channel** - Regular formatted posts with rich blocks
2. **Figma Channel** - Plain text format with hashtags for Figma integration

## Setup Instructions

### 1. Create Slack Webhooks

Create two different webhooks in your Slack workspace:

1. **Default Channel Webhook** (e.g., `#curated-posts`)
   - Go to Slack App settings
   - Create a new webhook for your default channel
   - Copy the webhook URL

2. **Figma Channel Webhook** (e.g., `#figma-ready`)
   - Create another webhook for your Figma channel
   - Copy the webhook URL

### 2. Environment Variables

Add these to your `.env` file in the backend directory:

```env
# OpenAI API Key for AI editing
OPENAI_API_KEY=your_openai_api_key_here

# Slack Webhook URLs for dual-channel posting
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
SLACK_WEBHOOK_FIGMA_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ

```
**Note**: Keep these webhook URLs private and do not share them publicly.

### 3. API Endpoints

The system now provides two endpoints:

- `POST /slack/{story_id}` - Posts to default channel with rich formatting
- `POST /slack-figma/{story_id}` - Posts to Figma channel with hashtag format

### 4. Frontend Buttons

When a story is edited, you'll see two buttons:

- **📤 Send to Slack** - Posts to default channel
- **🪄 Send Figma Format** - Posts to Figma channel

## Figma Format

The Figma format posts plain text with hashtags:

```
#title
Your Article Title

#date
January 15, 2024

#body
Your edited article content here...

#link
https://original-article-link.com
```

## Testing

1. Start your backend server
2. Start your frontend
3. Select and edit a story
4. Try both posting buttons
5. Check both Slack channels for the posts

## Troubleshooting

- Ensure both webhook URLs are valid and active
- Check that the channels exist and the webhooks have posting permissions
- Verify environment variables are loaded correctly
- Check backend logs for any webhook posting errors 