from dotenv import load_dotenv
load_dotenv()

from crewai import Crew
from tasks import plan_task, teach_task, exercise_task, motivate_task
from agents import planner_agent, teacher_agent, exercise_agent, motivator_agent
from telegram_bot import send_telegram_message
import os
import json
from datetime import datetime
import pytz
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def run_crew():
    crew = Crew(
        agents=[planner_agent, teacher_agent, exercise_agent, motivator_agent],
        tasks=[plan_task, teach_task, exercise_task, motivate_task],
        verbose=True
    )
    return crew.kickoff()

def main():
    # Get today in Berlin time
    berlin = pytz.timezone('Europe/Berlin')
    today = datetime.now(berlin).strftime('%Y-%m-%d')

    # Load progress
    with open('progress.json', 'r') as f:
        progress = json.load(f)

    # Run the crew with retry
    result = run_crew()

    # Assuming result is a list of task outputs in order
    plan = str(result[0])
    lesson = str(result[1])
    exercise = str(result[2])
    motivation = str(result[3])

    # Compile the daily message
    message = f"درس روزانه پایتون:\n\n{lesson}\n\nتمرین:\n{exercise}\n\n{motivation}"

    # Send via Telegram
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    send_telegram_message(token, chat_id, message)

    # Update progress
    progress['last_sent_date'] = today
    with open('progress.json', 'w') as f:
        json.dump(progress, f, indent=4)

if __name__ == "__main__":
    main()