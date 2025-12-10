# PythonMasterAgent_DeepSeek

A personal Python coach bot that runs 24/7 and sends daily lessons via Telegram using AI agents.

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
     - Get Together.ai API key from https://together.ai/ (for DeepSeek, Mistral, Qwen)
     - Get HuggingFace API key from https://huggingface.co/settings/tokens
     - Get OpenRouter API key from https://openrouter.ai/
     - Create a Telegram bot: talk to @BotFather on Telegram, get token
     - Get your chat ID: send a message to your bot, then curl https://api.telegram.org/bot<TOKEN>/getUpdates

6. **Make run_bot.sh executable:**
   ```
   chmod +x run_bot.sh
   ```

7. **Test the bot:**
   ```
   bash run_bot.sh
   ```
   This will start the bot, which listens for messages and sends daily lessons at 08:00 Berlin time.

8. **Set up as a systemd service for 24/7 running:**
   - Create service file: `sudo nano /etc/systemd/system/pythonmasteragent.service`
     ```
     [Unit]
     Description=PythonMasterAgent Bot
     After=network.target

     [Service]
     Type=simple
     User=your_user
     WorkingDirectory=/path/to/PythonMasterAgent_DeepSeek
     ExecStart=/path/to/PythonMasterAgent_DeepSeek/run_bot.sh
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Reload systemd: `sudo systemctl daemon-reload`
   - Enable: `sudo systemctl enable pythonmasteragent`
   - Start: `sudo systemctl start pythonmasteragent`
   - Check status: `sudo systemctl status pythonmasteragent`

9. **Note on time:**
   - Ensure server time is set to Berlin timezone: `sudo timedatectl set-timezone Europe/Berlin`

## Usage
- The bot sends daily lessons at 08:00 Berlin time.
- Reply with "done" to mark the lesson as completed.
- All content is in Persian.

## Notes
- Uses DeepSeek-Coder-V2 for most tasks.
- Auto-retries on API failures.
- Tracks 10-week curriculum and progress.