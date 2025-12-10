from langchain_groq import ChatGroq
from langchain_together import ChatTogether
from langchain_huggingface import ChatHuggingFace
from langchain_openai import ChatOpenAI
from crewai import Agent
import os

# Define LLMs
deepseek = ChatTogether(model="deepseek-ai/DeepSeek-Coder-V2-Instruct", api_key=os.getenv("TOGETHER_API_KEY"))
groq_405b = ChatGroq(model="llama-3.1-405b-instruct", api_key=os.getenv("GROQ_API_KEY"))
together_mistral = ChatTogether(model="mistralai/Mistral-Large-v2", api_key=os.getenv("TOGETHER_API_KEY"))
together_qwen = ChatTogether(model="Qwen/Qwen2-72B-Instruct", api_key=os.getenv("TOGETHER_API_KEY"))
hf_phi3 = ChatHuggingFace(model="microsoft/Phi-3-medium-4k-instruct", api_key=os.getenv("HUGGINGFACE_API_KEY"))
hf_gemma = ChatHuggingFace(model="google/gemma-2-9b-it", api_key=os.getenv("HUGGINGFACE_API_KEY"))
openrouter = ChatOpenAI(model="openai/gpt-3.5-turbo", api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

# Define Agents
planner_agent = Agent(
    role="Planner",
    goal="Create a 10-week Python curriculum if not exists, choose today's topic based on progress, and update tracking.",
    backstory="You are an expert curriculum designer for Python learning.",
    llm=deepseek,
    verbose=True
)

teacher_agent = Agent(
    role="Teacher",
    goal="Write the full lesson in clean, friendly, motivational Persian.",
    backstory="You teach Python engagingly in Persian.",
    llm=deepseek,
    verbose=True
)

exercise_agent = Agent(
    role="Exercise Creator",
    goal="Create one real-world 30-minute project/exercise with full solution and test cases.",
    backstory="You create practical coding exercises.",
    llm=deepseek,
    verbose=True
)

motivator_agent = Agent(
    role="Motivator",
    goal="Read progress, send encouragement in Persian, or funny roast if days skipped.",
    backstory="You motivate learners in Persian with humor.",
    llm=groq_405b,
    verbose=True
)