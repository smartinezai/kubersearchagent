import asyncio
import streamlit as st
import ingest
import search_agent
import logs


REPO_OWNER = "kubernetes"
REPO_NAME = "website"


@st.cache_resource
def init_agent():
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

# --- Streaming helper ---
def stream_response(prompt: str):
    async def agen():
        async with agent.run_stream(user_prompt=prompt) as result:
            last_len = 0
            full_text = ""
            async for chunk in result.stream_output(debounce_by=0.01):
                new_text = chunk[last_len:]
                last_len = len(chunk)
                full_text = chunk
                if new_text:
                    yield new_text
            logs.log_interaction_to_file(agent, result.new_messages())
            st.session_state._last_response = full_text

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agen_obj = agen()
    try:
        while True:
            piece = loop.run_until_complete(agen_obj.__anext__())
            yield piece
    except StopAsyncIteration:
        return


# --- Chat input ---
if prompt := st.chat_input("Ask your Kubernetes question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = st.write_stream(stream_response(prompt))

    final_text = getattr(st.session_state, "_last_response", response_text)
    st.session_state.messages.append({"role": "assistant", "content": final_text})