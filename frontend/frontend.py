import streamlit as st
import uuid
from chatbot.chatbot import retrieve_all_threads,loadConv
from langchain_core.messages import HumanMessage
from backend.main import main
from chatbot.chatbot import chatBot

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


# Session state 
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = retrieve_all_threads()

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
            main(video_id,"youtube",st.session_state.thread_id)
            st.success("Video ID extracted")
            st.write(video_id)

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
            main(upload_files,"video",st.session_state.thread_id)
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
            main(upload_files,"audio",st.session_state.thread_id)
            st.success(f"{len(upload_files)} audio file(s) uploaded ")

#Text Summarizer 
if st.session_state.mode == "text":
    text_input = st.text_area("Enter text to summarize")

    if st.button("Submit"):
        if not text_input.strip():
            st.error("Please enter some text")
        else:
            main(text_input,"text",st.session_state.thread_id)
            st.success("Text received")







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

        # Placeholder for assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            # Simulate thinking process
            response_placeholder.markdown("...thinking...")

            # Here you would integrate the chatbot response generation
            # For demonstration, we will just echo the user input
            assistant_response = chatBot.invoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG
            )["messages"][-1].content
            # Update the placeholder with the actual response
            response_placeholder.markdown(assistant_response)

        # Append assistant response to message history
        st.session_state.message_history.append({"role": "assistant", "content": assistant_response})
