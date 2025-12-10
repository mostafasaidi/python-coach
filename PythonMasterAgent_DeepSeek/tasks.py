from crewai import Task
from agents import planner_agent, teacher_agent, exercise_agent, motivator_agent
import json

# Load progress
with open('progress.json', 'r') as f:
    progress = json.load(f)

# Define Tasks
plan_task = Task(
    description=f"If curriculum is empty, create a detailed 10-week Python learning curriculum from beginner to advanced. Then, based on current_week {progress['current_week']} and current_day {progress['current_day']}, select today's topic and provide a brief plan.",
    agent=planner_agent,
    expected_output="Curriculum list if created, and today's topic with plan."
)

teach_task = Task(
    description="Using the topic and plan, write the complete lesson in clean, friendly, motivational Persian.",
    agent=teacher_agent,
    context=[plan_task],
    expected_output="Full lesson text in Persian."
)

exercise_task = Task(
    description="Based on the lesson, create one real-world 30-minute project/exercise with full solution code and test cases.",
    agent=exercise_agent,
    context=[teach_task],
    expected_output="Exercise description, solution code, and test cases."
)

motivate_task = Task(
    description=f"Review progress: {progress}. If the previous day was completed, send encouragement in Persian. If skipped, give a funny roast in Persian.",
    agent=motivator_agent,
    expected_output="Motivational message in Persian."
)