import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="APEX Cloud Agent",
    page_icon="🌐",
    layout="centered"
)

st.markdown("""
<style>
    .stApp { background-color: #1A1A2E; }
    h1 { color: #4285F4; }
    .subtitle { color: #8AB4F8; font-size: 1rem; margin-top: -10px; margin-bottom: 20px; }
    .tool-badge {
        display: inline-block; padding: 3px 10px; border-radius: 12px;
        background: #16213E; color: #4285F4; border: 1px solid #4285F4;
        font-size: 0.75rem; margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("# APEX Cloud Agent")
st.markdown('<div class="subtitle">Powered by Groq · Deployed on Render</div>', unsafe_allow_html=True)
st.markdown("""
<span class="tool-badge">Web Search</span>
<span class="tool-badge">Weather</span>
<span class="tool-badge">Calculator</span>
""", unsafe_allow_html=True)

st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask APEX anything...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("APEX is thinking..."):
            try:
                response = run_agent(user_input)
            except Exception as e:
                response = f"Error: {str(e)}"
        st.markdown(response)
        st.session_state.history.append({"role": "assistant", "content": response})

with st.sidebar:
    st.markdown("### About APEX")
    st.markdown("**W301** · Wave 3 · Cloud Agent")
    st.markdown("Deployed on Render via Docker.")
    st.divider()
    st.markdown("**Tools**")
    st.markdown("- Web Search (Serper)")
    st.markdown("- Weather (wttr.in)")
    st.markdown("- Calculator")
    st.divider()
    if st.button("Clear chat"):
        st.session_state.history = []
        st.rerun()
