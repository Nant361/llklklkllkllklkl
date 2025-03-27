# Telegram Student Search Bot

A Telegram bot for searching student information from PDDikti database.

## Deployment on Koyeb

1. Fork this repository to your GitHub account

2. Sign up for a Koyeb account at https://app.koyeb.com

3. Create a new app on Koyeb:
   - Click "Create App"
   - Choose "GitHub" as your deployment method
   - Select your forked repository
   - Choose the branch you want to deploy (usually `main` or `master`)
   - Select "Python" as your buildpack
   - Click "Deploy"

4. Configure environment variables in Koyeb:
   - Go to your app's settings
   - Navigate to "Environment Variables"
   - Add the following variables:
     ```
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     ADMIN_BOT_TOKEN=your_admin_bot_token
     ADMIN_CHAT_ID=your_admin_chat_id
     ```

5. The bot will automatically start after deployment

## Local Development

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your environment variables:
   ```bash
   cp .env.example .env
   ```

5. Run the bot:
   ```bash
   python main.py
   ```

## Features

- Search student information by name or NIM
- View detailed student information
- Admin panel for user management
- Activity logging
- User registration system

## Security Notes

- Never commit your `.env` file or expose your bot tokens
- Keep your admin credentials secure
- Regularly update dependencies for security patches

## Support

For support, contact @nant12_bot on Telegram. 