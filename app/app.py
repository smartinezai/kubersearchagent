import os
import asyncio
import streamlit as st
import ingest
import search_agent
import logs


REPO_OWNER = "kubernetes"
REPO_NAME = "website"


@st.cache_resource
def init_agent():
    # Read API key from Streamlit secrets or environment
    try:
        groq_key = st.secrets.get("GROQ_API_KEY")
    except Exception:
        groq_key = None
    groq_key = groq_key or os.getenv("GROQ_API_KEY")
    if not groq_key:
        st.error("GROQ_API_KEY not found in secrets!")
        st.stop()
    os.environ["GROQ_API_KEY"] = groq_key

    st.write("🔄 Downloading and indexing Kubernetes docs (this may take a minute)...")
    index = ingest.index_data(REPO_OWNER, REPO_NAME)
    agent = search_agent.init_agent(index, REPO_OWNER, REPO_NAME)
    st.write("✅ Ready!")
    return agent


agent = init_agent()

# --- Streamlit UI ---
st.set_page_config(page_title="Kubernetes AI Assistant", page_icon="☸️", layout="centered")
st.title("☸️ Kubernetes AI Assistant")
st.caption("Ask me anything about Kubernetes — powered by the official docs")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat input ---
if prompt := st.chat_input("Ask your Kubernetes question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(agent.run(user_prompt=prompt))
            answer = response.output
            logs.log_interaction_to_file(agent, response.new_messages())
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})