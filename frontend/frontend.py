import streamlit as st

st.title("Welcome to Q&A Chatbot")

# -------- Session state --------
if "mode" not in st.session_state:
    st.session_state.mode = None

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

# -------- YouTube Transcript --------
if st.session_state.mode == "youtube":
    lnk = st.text_input(
        "Enter the YouTube link here...",
        placeholder="Example: https://www.youtube.com/watch?v=AbC123XyZ90"
    )

    if st.button("Submit"):
        if not lnk:
            st.error("Please enter a YouTube link ❌")
        else:
            video_id = lnk.split("=")[-1]
            st.success("Video ID extracted ✅")
            st.write(video_id)

# -------- Video Summarizer --------
if st.session_state.mode == "video":
    upload_files = st.file_uploader(
        "Choose video files",
        type=["mp4"],
        accept_multiple_files=True
    )

    if st.button("Submit"):
        if not upload_files:
            st.error("Please upload at least one video ❌")
        else:
            st.success(f"{len(upload_files)} video(s) uploaded ✅")

# -------- Audio Summarizer --------
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
            st.success(f"{len(upload_files)} audio file(s) uploaded ")

#Text Summarizer 
if st.session_state.mode == "text":
    text_input = st.text_area("Enter text to summarize")

    if st.button("Submit"):
        if not text_input.strip():
            st.error("Please enter some text ❌")
        else:
            st.success("Text received")
