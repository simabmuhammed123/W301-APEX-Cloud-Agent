import os
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

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
    """Get current weather for a city."""
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=10)
        return response.text.strip()
    except Exception as e:
        return f"Weather error: {str(e)}"

def calculate(expression: str) -> str:
    """Evaluate a math expression safely."""
    try:
        allowed = set("0123456789+-*/().,% ")
        if not all(c in allowed for c in expression):
            return "Only basic math expressions are allowed."
        result = eval(expression)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

TOOLS_MAP = {
    "web_search": web_search,
    "get_weather": get_weather,
    "calculate": calculate,
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information on any topic.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "Math expression"}},
                "required": ["expression"],
            },
        },
    },
]

SYSTEM_PROMPT = """You are APEX — a powerful cloud-deployed AI assistant.
You have access to three tools:
1. web_search — use for current events, facts, or research
2. get_weather — use when asked about weather in any city
3. calculate — use for any math calculations
Always use tools when needed. Be concise and helpful.
If asked who you are, say you are APEX, a cloud-deployed AI agent."""

def run_agent(user_input: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ]
    import json
    for _ in range(5):
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [tc.model_dump() for tc in msg.tool_calls]})
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                result = TOOLS_MAP[fn_name](**fn_args)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
        else:
            return msg.content or "No response."
    return "Max iterations reached."
