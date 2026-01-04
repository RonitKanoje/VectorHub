import streamlit as st
import uuid
from chatbot.chatbot import retrieve_all_threads,loadConv
from langchain_core.messages import HumanMessage
from backend.main import main       
import requests
import os 

st.title("Welcome to Q&A Chatbot")

### Defining Function 
def generate_thread_id():
    return str(uuid.uuid4())

def addThread(thread_id):
    if thread_id not in st.session_state.chat_threads:
        st.session_state.chat_threads.append(thread_id)

def resetChat():
    st.session_state.message_history = []
    st.session_state.thread_id = generate_thread_id()
    addThread(st.session_state.thread_id)

def loadChat(thread_id):
    messages = loadConv(thread_id)
    return messages

def wait_until_ready(thread_id):
    with st.spinner("Processing your documents..."):
        while True:
            res = requests.get(f"{API_BASE_URL}/thread_status/{thread_id}")

            if res.status_code != "completed":
                st.error("Error checking thread status")

            status = res.json()["status"]

            if status == "completed":
                break


# Session state 
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

API_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")

if "chat_threads" not in st.session_state:
    response = requests.get(f"{API_BASE_URL}/threads")

    if response.status_code == 200:
        st.session_state.chat_threads = response.json()["threads"]
    else:
        st.session_state.chat_threads = []
        st.error("Failed to load chat threads")

if "mode" not in st.session_state:
    st.session_state.mode = None

if "submit" not in st.session_state:
    st.session_state.submit = False

CONFIG = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}


col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Youtube Transcript"):
        st.session_state.mode = "youtube"

with col2:
    if st.button("Video Summarizer"):
        st.session_state.mode = "video"

with col3:
    if st.button("Text Summarizer"):
        st.session_state.mode = "text"

with col4:
    if st.button("Audio Summarize"):
        st.session_state.mode = "audio"

# YouTube Transcript 
if st.session_state.mode == "youtube":
    lnk = st.text_input(
        "Enter the YouTube link here...",
        placeholder="Example: https://www.youtube.com/watch?v=AbC123XyZ90"
    )

    if st.button("Submit"):
        if not lnk:
            st.error("Please enter a YouTube link")
        else:
            video_id = lnk.split("=")[-1]
            st.session_state.submit = True 
            #main(video_id,"youtube",st.session_state.thread_id)
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": video_id,
                "media": "youtube",
                "thread_id": st.session_state.thread_id
            })
            st.success("Video ID extracted")
            st.write(video_id)
            st.write(st.session_state.thread_id)

# Video Summarizer 
if st.session_state.mode == "video":
    upload_files = st.file_uploader(
        "Choose video files",
        type=["mp4"],
        accept_multiple_files=True
    )

    if st.button("Submit"):
        if not upload_files:
            st.error("Please upload at least one video")
        else:
            # main(upload_files,"video",st.session_state.thread_id)
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": [f.name for f in upload_files],
                "media": "video",
                "thread_id": st.session_state.thread_id
            })
            st.session_state.submit = True 
            st.success(f"{len(upload_files)} video(s) uploaded")

# Audio Summarizer 
if st.session_state.mode == "audio":
    upload_files = st.file_uploader(
        "Choose audio files",
        type=["mp3"],
        accept_multiple_files=True
    )

    if st.button("Submit"):
        if not upload_files:
            st.error("Please upload at least one audio file")
        else:
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": [f.name for f in upload_files],
                "media": "audio",
                "thread_id": st.session_state.thread_id
            })
            st.session_state.submit = True 
            st.success(f"{len(upload_files)} audio file(s) uploaded ")

#Text Summarizer 
if st.session_state.mode == "text":
    text_input = st.text_area("Enter text to summarize")

    if st.button("Submit"):
        if not text_input.strip():
            st.error("Please enter some text")
        else:
            #main(text_input,"text",st.session_state.thread_id)
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": [text_input],
                "media": "text",
                "thread_id": st.session_state.thread_id
            })
            st.session_state.submit = True 
            st.success("Text received")



## Main UI
for msg in st.session_state.message_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

### Slider Bar for Chat History
st.sidebar.title("Chat History")

if st.sidebar.button("New Chat"):
    resetChat()

for thread in st.session_state.chat_threads:
    if st.sidebar.button(f"Chat {thread}"):
        st.session_state.thread_id = thread
        st.session_state.message_history = loadChat(thread)

        tempMsg = []

        for msg in st.session_state.message_history:
            if isinstance(msg, HumanMessage):
                tempMsg.append(({"role": "user", "content": msg.content}))
            else:
                tempMsg.append(({"role": "assistant", "content": msg.content}))
        st.session_state.message_history = tempMsg

### Chat Interface
if st.session_state.submit == True:
    user_input = st.chat_input("Type your message here...")

    

    if user_input:
        st.session_state.message_history.append({"role": "user", "content": user_input})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        wait_until_ready(st.session_state.thread_id)

        # Placeholder for assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            # Simulate thinking process
            response_placeholder.markdown("...thinking...")


        # Get assistant response from chatbot
            assistant_response = requests.post(os.getenv("FASTAPI_CHAT_URL"), json={
                "role": "user",
                "content": user_input,
                "thread_id": st.session_state.thread_id
            }).json()["response"]
            # Update the placeholder with the actual response
            response_placeholder.markdown(assistant_response)  

        # Append assistant response to message history
        st.session_state.message_history.append({"role": "assistant", "content": assistant_response})   