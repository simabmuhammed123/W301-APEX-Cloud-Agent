import os
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# LiteLLM reads these directly from os.environ
os.environ["GROQ_API_KEY"] = GROQ_API_KEY or ""

def web_search(query: str) -> str:
    """Search the web for current information on any topic."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": 5}
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        results = []
        for item in data.get("organic", [])[:5]:
            results.append(f"- {item.get('title')}: {item.get('snippet')}")
        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

def get_weather(city: str) -> str:
    """Get current weather information for a city."""
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=10)
        return response.text.strip()
    except Exception as e:
        return f"Weather error: {str(e)}"

def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    try:
        allowed = set("0123456789+-*/().,% ")
        if not all(c in allowed for c in expression):
            return "Only basic math expressions are allowed."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

model = LiteLlm(
    model="groq/meta-llama/llama-4-scout-17b-16e-instruct",
)

root_agent = Agent(
    name="W301_CloudAgent",
    model=model,
    description="A cloud-deployed AI agent with web search, weather, and calculator tools.",
    instruction="""You are APEX — a powerful cloud-deployed AI assistant.
You have access to three tools:
1. web_search — use this for any current events, facts, or research questions
2. get_weather — use this when the user asks about weather in any city
3. calculate — use this for any math calculations
Always think step by step. Use tools when needed. Be concise and helpful.
If asked who you are, say you are APEX, a cloud-deployed AI agent built on Google ADK.""",
    tools=[web_search, get_weather, calculate],
)
