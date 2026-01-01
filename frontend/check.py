import streamlit as st

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    user_input = st.text_input("Ask something")
    if st.button("Submit"):
        st.session_state.submitted = True
        st.write("Submitted!")
else:
    st.write("Input box removed")
