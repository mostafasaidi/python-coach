from crewai import Task
from agents import planner_agent, teacher_agent, exercise_agent, motivator_agent
import json

# Load progress
with open('progress.json', 'r') as f:
    progress = json.load(f)

# Define Tasks
plan_task = Task(
    description=f"Based on completed lessons: {progress['completed_lessons']}, choose an appropriate Python topic for today and create a 15-minute lesson plan.",
    agent=planner_agent,
    expected_output="Selected topic and detailed 15-minute lesson plan."
)

teach_task = Task(
    description="Using the plan from the Planner, write the full lesson in clean, friendly Persian.",
    agent=teacher_agent,
    context=[plan_task],
    expected_output="Complete lesson text in Persian."
)

exercise_task = Task(
    description="Based on the lesson, create one practical 30-minute Python exercise with a detailed solution.",
    agent=exercise_agent,
    context=[teach_task],
    expected_output="Exercise description and step-by-step solution."
)

motivate_task = Task(
    description=f"Review progress: {progress}. If the last lesson was sent today, send encouragement. Otherwise, a friendly roast in Persian.",
    agent=motivator_agent,
    expected_output="Motivational message in Persian."
)