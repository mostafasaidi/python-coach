# PythonMasterAgent

A personal Python coach bot that sends daily lessons via Telegram using AI agents.

## Setup Steps

1. **Clone or copy the project to your Ubuntu server:**
   ```
   # Assuming you have the files, place them in a directory
   ```

2. **Install Python 3.11+ if not already installed:**
   ```
   sudo apt update
   sudo apt install python3.11 python3.11-venv
   ```

3. **Create a virtual environment (optional but recommended):**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in your API keys:
     - Get Groq API key from https://console.groq.com/
     - Get Together.ai API key from https://together.ai/
     - Get HuggingFace API key from https://huggingface.co/settings/tokens
     - Get OpenRouter API key from https://openrouter.ai/
     - Create a Telegram bot: talk to @BotFather on Telegram, get token
     - Get your chat ID: send a message to your bot, then curl https://api.telegram.org/bot<TOKEN>/getUpdates

6. **Make run_daily.sh executable:**
   ```
   chmod +x run_daily.sh
   ```

7. **Test the script:**
   ```
   bash run_daily.sh
   ```
   This should send a lesson to your Telegram.

8. **Set up daily cron job for 08:00 Berlin time:**
   - Edit crontab: `crontab -e`
   - Add: `0 8 * * * /full/path/to/run_daily.sh`
   - Note: Ensure server time is set to Berlin timezone: `sudo timedatectl set-timezone Europe/Berlin`

9. **For 24/7 running (optional, since cron handles daily):**
   - Use systemd or screen/tmux if needed, but cron suffices for daily execution.

## Notes
- All lessons are in Persian.
- Code is in English.
- Auto-retries on API failures.