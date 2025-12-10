from langchain_groq import ChatGroq
from langchain_together import ChatTogether
from langchain_huggingface import ChatHuggingFace
from langchain_openai import ChatOpenAI
from crewai import Agent
import os

# Define LLMs
groq_llm_70b = ChatGroq(model="llama-3.1-70b-instruct", api_key=os.getenv("GROQ_API_KEY"))
groq_llm_405b = ChatGroq(model="llama-3.1-405b-instruct", api_key=os.getenv("GROQ_API_KEY"))
together_mistral = ChatTogether(model="mistralai/Mistral-Large-v2", api_key=os.getenv("TOGETHER_API_KEY"))
together_deepseek = ChatTogether(model="deepseek-ai/deepseek-coder-33b-instruct", api_key=os.getenv("TOGETHER_API_KEY"))
hf_phi3 = ChatHuggingFace(model="microsoft/Phi-3-medium-4k-instruct", api_key=os.getenv("HUGGINGFACE_API_KEY"))
openrouter_fallback = ChatOpenAI(model="openai/gpt-3.5-turbo", api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1")

# Define Agents
planner_agent = Agent(
    role="Planner",
    goal="Choose today's Python topic and create a 15-minute lesson plan",
    backstory="You are an expert Python educator who selects appropriate topics based on progress.",
    llm=together_mistral,
    verbose=True
)

teacher_agent = Agent(
    role="Teacher",
    goal="Write the actual lesson in clean, friendly Persian",
    backstory="You teach Python in an engaging, motivational way in Persian.",
    llm=groq_llm_70b,
    verbose=True
)

exercise_agent = Agent(
    role="Exercise Creator",
    goal="Create one 30-minute practical Python exercise with solution",
    backstory="You create hands-on coding exercises.",
    llm=together_deepseek,
    verbose=True
)

motivator_agent = Agent(
    role="Motivator",
    goal="Check progress and send encouragement or roast",
    backstory="You motivate the learner in Persian.",
    llm=groq_llm_405b,
    verbose=True
)