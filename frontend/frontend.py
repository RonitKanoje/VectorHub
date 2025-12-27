import streamlit as st

st.title("Welcome to Q&A Chatbot")
st.write("")

col1, col2, col3, col4 = st.columns(4)

with col1:
    yt_btn = st.button("Youtube Transcript")

with col2:
    video_btn = st.button("Video Summarizer")

with col3:
    text_btn = st.button("Text Summarizer")

with col4:
    audio_btn = st.button("Audio Summarize")


st.chat_input("Ask Your Question ....")