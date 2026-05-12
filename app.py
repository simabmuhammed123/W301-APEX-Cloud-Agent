import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from agent import root_agent

load_dotenv()

st.set_page_config(
    page_title="APEX Cloud Agent",
    page_icon="🌐",
    layout="centered"
)

st.markdown("""
<style>
    .main { background-color: #1A1A2E; }
    .stApp { background-color: #1A1A2E; }
    h1 { color: #4285F4; font-size: 2.2rem; }
    .subtitle { color: #8AB4F8; font-size: 1rem; margin-top: -10px; margin-bottom: 20px; }
    .tool-badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        background: #16213E; color: #4285F4; border: 1px solid #4285F4;
        font-size: 0.75rem; margin-right: 6px;
    }
    .response-box {
        background: #16213E; border-left: 3px solid #4285F4;
        padding: 16px; border-radius: 8px; color: #E8EAED;
        margin-top: 12px; white-space: pre-wrap;
    }
    .stTextArea textarea { background: #16213E; color: #E8EAED; border: 1px solid #4285F4; }
    .stButton button {
        background: #4285F4; color: white; border: none;
        padding: 10px 28px; border-radius: 8px; font-size: 1rem;
    }
    .stButton button:hover { background: #1A73E8; }
</style>
""", unsafe_allow_html=True)

st.markdown("# APEX Cloud Agent")
st.markdown('<div class="subtitle">Powered by Google ADK · Deployed on the cloud</div>', unsafe_allow_html=True)
st.markdown("""
<span class="tool-badge">Web Search</span>
<span class="tool-badge">Weather</span>
<span class="tool-badge">Calculator</span>
""", unsafe_allow_html=True)

st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

async def run_agent(user_input: str) -> str:
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="apex", user_id="user_01", session_id="session_01"
    )
    runner = Runner(
        agent=root_agent,
        app_name="apex",
        session_service=session_service,
    )
    content = types.Content(
        role="user",
        parts=[types.Part(text=user_input)]
    )
    final_response = ""
    async for event in runner.run_async(
        user_id="user_01",
        session_id="session_01",
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = event.content.parts[0].text
    return final_response

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask APEX anything — search, weather, math...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("APEX is thinking..."):
            try:
                response = asyncio.run(run_agent(user_input))
            except Exception as e:
                response = f"Error: {str(e)}"
        st.markdown(response)
        st.session_state.history.append({"role": "assistant", "content": response})

with st.sidebar:
    st.markdown("### About APEX")
    st.markdown("**W301** · Wave 3 · Google ADK")
    st.markdown("Cloud-deployed agent with real-time tools.")
    st.divider()
    st.markdown("**Tools available**")
    st.markdown("- Web Search (Serper)")
    st.markdown("- Weather (wttr.in)")
    st.markdown("- Calculator")
    st.divider()
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()
