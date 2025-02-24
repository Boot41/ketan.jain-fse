# Jira AI Assistant

A powerful integration between Jira and OpenAI that helps streamline your project management workflow using AI capabilities.

## Table of Contents
- [Prerequisites](#prerequisites)
- [API Keys Setup](#api-keys-setup)
  - [Jira API Token](#jira-api-token)
  - [OpenAI API Key](#openai-api-key)
- [Local Development Setup](#local-development-setup)
- [Docker Setup](#docker-setup)
- [Environment Variables](#environment-variables)

## Prerequisites

- Python 3.12 or higher
- Node.js 20 or higher
- Docker and Docker Compose (for containerized deployment)
- Jira account with administrative access
- OpenAI account

## API Keys Setup

### Jira API Token

1. Log in to your Atlassian account at https://id.atlassian.com/manage/api-tokens
2. Click on "Create API token"
3. Give your token a name (e.g., "Jira AI Assistant")
4. Click "Create" and copy the generated token
5. Store this token securely - you won't be able to see it again

You'll also need:
- Your Jira instance URL (e.g., `https://your-domain.atlassian.net`)
- Your Jira email address

### OpenAI API Key

1. Visit https://platform.openai.com/account/api-keys
2. Log in to your OpenAI account
3. Click on "Create new secret key"
4. Give your key a name (optional)
5. Copy the generated API key
6. Store this key securely - you won't be able to see it again

## Local Development Setup

### Backend Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd JiraAIAssistant
   ```

2. Create and activate a virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your API keys and configuration (see [Environment Variables](#environment-variables) section)

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Docker Setup

1. Ensure Docker and Docker Compose are installed on your system

2. Configure environment variables:
   ```bash
   cd backend
   cp .env.example .env
   ```
   Edit the `.env` file with your API keys and configuration

3. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- Frontend: http://localhost:80
- Backend API: http://localhost:8000

## Environment Variables

Configure the following environment variables in the `backend/.env` file:

```env
# Django settings
DJANGO_SECRET_KEY="your-secret-key"

# OpenAI settings
OPENAI_API_KEY=your-openai-api-key-here

# Jira settings
JIRA_API_TOKEN=your-jira-api-token-here
JIRA_SERVER_URL=your-jira-instance-url
JIRA_USER_EMAIL=your-jira-email@example.com
```

### Environment Variables Description

- `DJANGO_SECRET_KEY`: A secret key for Django's cryptographic signing
- `OPENAI_API_KEY`: Your OpenAI API key
- `JIRA_API_TOKEN`: Your Jira API token
- `JIRA_SERVER_URL`: Your Jira instance URL (e.g., https://your-domain.atlassian.net)
- `JIRA_USER_EMAIL`: The email address associated with your Jira account

## Usage

Once the application is running, you can:
1. Access the web interface through your browser
2. Log in with your credentials
3. Start interacting with the AI assistant to manage your Jira tasks

## Security Notes

- Never commit your `.env` file or any API keys to version control
- Keep your API keys secure and rotate them periodically
- Use environment-specific settings for different deployment environments