import streamlit as st
import uuid
import requests
import os 
from frontend.languages import WHISPER_LANGUAGES
import shutil
from dotenv import load_dotenv

load_dotenv()

st.title("Welcome to Q&A Chatbot")

### Defining Function 
def generate_thread_id():
    return str(uuid.uuid4())

def addThread(thread_id):
    thread_dict = {
        "thread_id": thread_id,
        "title": "New Chat"
    }
    # Check if thread_id already exists
    existing_ids = [t['thread_id'] for t in st.session_state.chat_threads]
    if thread_id not in existing_ids:
        st.session_state.chat_threads.append(thread_dict)

def resetChat():
    st.session_state.message_history = []
    st.session_state.thread_id = {
        "thread_id": generate_thread_id(),
        "title": "New Chat"    
    }
    addThread(st.session_state.thread_id["thread_id"])
    st.session_state.submit = False
    st.rerun()

def loadChat(thread_id):
    st.session_state.submit = True
    response = requests.get(f"{API_BASE_URL}/loadConv/{thread_id}")
    response.raise_for_status()     
    return response.json()['messages']

def wait_until_ready(thread_id):
    with st.spinner("Processing your documents..."):
        while True:
            res = requests.get(f"{API_BASE_URL}/thread_status/{thread_id}")

            if res.status_code != "completed":
                st.spinner("Response is generating")

            status = res.json()["status"]

            if status == "completed":
                if st.session_state.mode == "video":
                    audio_dir = "backend/videobackend/tmp/audios"
                    video_dir = "backend/videobackend/tmp/videos"

                    if os.path.exists(audio_dir):
                        shutil.rmtree(audio_dir)

                    if os.path.exists(video_dir):
                        shutil.rmtree(video_dir)
                break

# Session state 

if not st.session_state.authenticated:
    st.warning("Please login first.")
    st.switch_page("pages/1_Authentication.py")
    st.stop()


if "user_id" not in st.session_state:
    st.warning("Please login first.")
    st.switch_page("pages/1_Authentication.py")


if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = {'thread_id' : generate_thread_id(),
                                  'title' : "New Chat"}

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
        "thread_id": st.session_state.thread_id["thread_id"]
    }
}


col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Youtube Transcript",disabled=st.session_state.submit):
        st.session_state.mode = "youtube"

with col2:
    if st.button("Video Summarizer",disabled=st.session_state.submit):
        st.session_state.mode = "video"

with col3:
    if st.button("Text Summarizer",disabled=st.session_state.submit):
        st.session_state.mode = "text"

with col4:
    if st.button("Audio Summarize",disabled=st.session_state.submit):
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
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": video_id,
                "media": "youtube",
                "thread_id": st.session_state.thread_id["thread_id"]
            })
            st.success("Video ID extracted")
            st.write(video_id)
            st.write(st.session_state.thread_id["thread_id"])

# Video Summarizer 
if st.session_state.mode == "video":
    upload_file = st.file_uploader(
        "Choose video files",
        type="mp4",
        accept_multiple_files=False
    )
    lang = st.selectbox(
        "Select the language of the video content (optional)",
        options=["None"] + list(WHISPER_LANGUAGES.values())
    )
    for lang_code, lang_name in WHISPER_LANGUAGES.items():
        if lang == lang_name:
            lang = lang_code
            break

    if st.button("Submit"):
        if not upload_file:
            st.error("Please upload at least one video")
        else:
            save_dir = 'backend/videobackend/tmp/videos'
            os.makedirs(save_dir, exist_ok=True)
            video_path = os.path.join(save_dir, f'{st.session_state.thread_id["thread_id"]}_{upload_file.name}')
            with open(video_path, 'wb') as f:
                f.write(upload_file.getbuffer())
            
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": video_path,
                "media": "video",
                "thread_id": st.session_state.thread_id["thread_id"],
                "language": None if lang == "None" else lang
            })
            st.session_state.submit = True 
            st.write(st.session_state.thread_id["thread_id"])

# Audio Summarizer 
if st.session_state.mode == "audio":
    upload_file = st.file_uploader(
        "Choose audio files",
        type="mp3",
        accept_multiple_files=False
    )

    if st.button("Submit"):
        if not upload_file:
            st.error("Please upload at least one audio file")
        else:
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": upload_file,
                "media": "audio",
                "thread_id": st.session_state.thread_id["thread_id"]
            })
            st.session_state.submit = True 

#Text Summarizer 
if st.session_state.mode == "text":
    text_input = st.text_area("Enter text For Q&A")

    if st.button("Submit"):
        if not text_input.strip():
            st.error("Please enter some text")
        else:
            requests.post(os.getenv("FASTAPI_PROCESS_URL"), json={
                "path": text_input,
                "media": "text",
                "thread_id": st.session_state.thread_id["thread_id"]
            })
            st.session_state.submit = True 
            st.success("Text received")
            st.write(st.session_state.thread_id["thread_id"])


### Slider Bar for Chat History
st.sidebar.title("Chat History")

if st.sidebar.button("New Chat"):
    resetChat()

for thread in st.session_state.chat_threads:
    if st.sidebar.button(f"{thread['title'][:20]}...",key=thread['thread_id']):
        st.session_state.thread_id = thread
        messages = loadChat(thread['thread_id']) 
        st.session_state.message_history = messages
        if len(messages) != 0:
            st.session_state.submit = True
        st.rerun() 

## Main UI
for msg in st.session_state.message_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

### Chat Interface
if st.session_state.submit == True:
    user_input = st.chat_input("Type your message here...")
    if user_input:
        if st.session_state.thread_id['title'] == "New Chat":
            res = requests.post(os.getenv("FASTAPI_NAMECHAT_URL"), json={
                "message": user_input,
                "thread_id": st.session_state.thread_id["thread_id"]
            })

            print("NameChat status:", res.status_code)

            if res.status_code == 200:
                st.session_state.thread_id['title'] = res.json()['title']

        st.session_state.message_history.append({"role": "user", "content": user_input})

        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            wait_until_ready(st.session_state.thread_id["thread_id"])
        except Exception as e:
            st.error("Kindly upload the video")
            st.session_state.submit = False
            st.stop()

        # Placeholder for assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()

            # Simulate thinking process
            response_placeholder.markdown("...thinking...")

            try:
                # Get assistant response from chatbot
                response = requests.post(
                    os.getenv("FASTAPI_CHAT_URL"), 
                    json={
                        "role": "user",
                        "content": user_input,
                        "thread_id": st.session_state.thread_id["thread_id"]
                    },
                    timeout=240  # Add timeout
                )
                
                # Check if request was successful
                response.raise_for_status()
                
                # Try to parse JSON
                assistant_response = response.json()["response"]
                
                # Update the placeholder with the actual response
                response_placeholder.markdown(assistant_response)
                
                # Append assistant response to message history
                st.session_state.message_history.append({
                    "role": "assistant", 
                    "content": assistant_response
                })
                
            except requests.exceptions.JSONDecodeError:
                error_msg = f"**Error**: Server returned invalid response\n\n```\n{response.text[:500]}\n```"
                response_placeholder.markdown(error_msg)
                st.error(f"Response status: {response.status_code}")
                
            except requests.exceptions.HTTPError as e:
                response_placeholder.markdown(f"**HTTP Error**: {e}")
                st.error(f"Status code: {response.status_code}")
                
            except requests.exceptions.Timeout:
                response_placeholder.markdown("**Error**: Request timed out")
                
            except requests.exceptions.RequestException as e:
                response_placeholder.markdown(f"**Error**: {str(e)}")