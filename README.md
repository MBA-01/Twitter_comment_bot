# Twitter Auto-Comment Bot

## Description
This bot automatically comments on tweets from your Twitter following feed using Selenium WebDriver. It includes features like daily comment limits, random delays between actions, and comment history tracking to avoid duplicate responses.

## Prerequisites

### Required Python Version
- Python 3.6 or higher

### Required Python Packages
   
bash : """  
pip install selenium   
pip install openai  
"""  
  
### Required Technologies
1. Chrome Browser (latest version recommended)
2. ChromeDriver
   - Must match your Chrome browser version
   - Download from: [ChromeDriver Official Site](https://sites.google.com/chromium.org/driver/)
   - Place `chromedriver.exe` in the same directory as the script

### API Keys
1. OpenAI API Key (Currently commented out in the code, but required if you uncomment the AI response generation)

## Configuration

### Required Credentials
Edit these variables in the script:

   
python : """   
USERNAME = "EMAIL" # Your Twitter email   
PASSWORD = "PASSWORD" # Your Twitter password   
MY_TWITTER_HANDLE = "USERNAME" # Your Twitter username   
openai.api_key = "key" # Your OpenAI API key (if using AI responses)   
""""   
 
### Customizable Parameters
- `MAX_DAILY_COMMENTS`: Maximum comments per day (default: 500)
- `COMMENT_DELAY`: Delay between comments (default: 15 seconds)
- `SESSION_DURATION`: How long the session runs (default: 6 hours)
- `MIN_WAIT_TIME`: Minimum wait time between actions (default: 15 seconds)
- `MAX_WAIT_TIME`: Maximum wait time between actions (default: 30 seconds)

## File Structure
  
project_directory/   
│   
├── twitter_bot_comment.py   
├── chromedriver.exe   
├── comment_history_{timestamp}.json # Generated automatically   
└── twitter_bot_{timestamp}.log # Generated automatically   
  
## Usage

1. Ensure all prerequisites are installed
2. Configure your credentials in the script
3. Place ChromeDriver in the correct location
4. Run the script:

bash : """  
python twitter_bot_comment.py  
"""

## Features
- Automatic login to Twitter
- Comments on posts in Following feed
- Avoids duplicate comments using comment history
- Random delays between actions to avoid detection
- Automatic session management
- Comprehensive logging
- Graceful error handling
- Daily comment limits

## Safety Features
- Skips own posts
- Maintains comment history
- Implements random delays
- Handles connection issues
- Graceful shutdown with Ctrl+C

## Troubleshooting

### Common Issues
1. ChromeDriver errors:
   - Ensure ChromeDriver version matches your Chrome browser version
   - Verify chromedriver.exe is in the correct location

2. Login failures:
   - Check your credentials
   - Verify your internet connection
   - Make sure your account isn't locked or requiring verification

3. Selenium errors:
   - Update Selenium to the latest version
   - Update ChromeDriver and Chrome browser

## Important Notes
- The AI response generation is currently commented out. Uncomment and configure OpenAI API key to enable AI-generated responses
- Twitter may detect automated behavior if the bot is used too aggressively
- Adjust timing parameters based on your needs and to avoid detection
- Keep your credentials secure and never share them in the code

## Disclaimer
This bot is for educational purposes. Be sure to comply with Twitter's terms of service and API usage guidelines when using automated tools.