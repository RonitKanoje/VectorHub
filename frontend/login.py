import streamlit as st
import requests
import re

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Authentication System",
    page_icon="🔐",
    layout="centered"
)

API_BASE_URL = "http://localhost:8000"

# -------------------------------------------------
# Utility: Password Validation (Frontend Only)
# -------------------------------------------------
def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return "Must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Must contain at least one lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Must contain at least one number."
    return None

# -------------------------------------------------
# Session State Initialization
# -------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None

if "page" not in st.session_state:
    st.session_state.page = "Login"

# -------------------------------------------------
# Signup Page
# -------------------------------------------------
def signup_page():
    st.title("📝 Create Account")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if not username or not password:
            st.error("All fields are required.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        validation_error = validate_password(password)
        if validation_error:
            st.warning(validation_error)
            return

        try:
            res = requests.post(
                f"{API_BASE_URL}/register",
                json={
                    "username": username,
                    "password": password
                }
            )

            if res.status_code == 200:
                st.success("Account created successfully! Please login.")
                st.session_state.page = "Login"
                st.rerun()
            else:
                st.error(res.json().get("detail", "Registration failed"))

        except Exception as e:
            st.error(f"Server error: {e}")

    if st.button("Already have an account? Login"):
        st.session_state.page = "Login"
        st.rerun()

# -------------------------------------------------
# Login Page
# -------------------------------------------------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if not username or not password:
            st.error("All fields are required.")
            return

        try:
            res = requests.post(
                f"{API_BASE_URL}/login",
                json={
                    "username": username,
                    "password": password
                }
            )

            if res.status_code == 200:
                data = res.json()
                st.session_state.authenticated = True
                st.session_state.user_id = data["user_id"]
                st.session_state.username = data["username"]

                st.success("Login successful!")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Invalid username or password"))

        except Exception as e:
            st.error(f"Server error: {e}")

    if st.button("Create new account"):
        st.session_state.page = "Signup"
        st.rerun()

# -------------------------------------------------
# Dashboard
# -------------------------------------------------
def dashboard():
    st.success(f"Welcome, {st.session_state.username} 🚀")
    st.write("You are logged in successfully.")

    st.divider()
    st.subheader("Dashboard Area")
    st.write("This is where your AI chatbot will load.")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.session_state.username = None
        st.session_state.page = "Login"
        st.rerun()

# -------------------------------------------------
# Main Router
# -------------------------------------------------
if not st.session_state.authenticated:
    if st.session_state.page == "Login":
        login_page()
    else:
        signup_page()
else:
    dashboard()