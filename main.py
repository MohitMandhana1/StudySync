import streamlit as st
import time
import pandas as pd
import hashlib

# Initialize session state if not already initialized
if "accounts" not in st.session_state:
    st.session_state["accounts"] = {}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "subjects" not in st.session_state:
    st.session_state["subjects"] = {}
if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if "studying" not in st.session_state:
    st.session_state["studying"] = False
if "message" not in st.session_state:
    st.session_state["message"] = ""

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def format_time(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds // 60} minutes"
    else:
        return f"{seconds // 3600} hours"

def login_page():
    st.title("StudySync")
    st.markdown("""
       <h3 style="font-size: 24px;">Welcome to the <strong>StudySync</strong>!</h3>
       <p style="font-size: 18px;">This app helps you track and manage your study sessions. 
       You can create an account, log in, add subjects, and track the time spent on each subject. 
       Stay focused, track your progress, and improve your study habits!</p>
       """, unsafe_allow_html=True)
    action = st.radio("Are you here for the first time?", ["Login", "Create Account"])

    if action == "Login":
        user_id = st.text_input("Enter your desired User ID")
        password = st.text_input("Enter your Password", type="password")
        if st.button("Login"):
            if user_id in st.session_state["accounts"]:
                hashed_password = hash_password(password)
                if st.session_state["accounts"][user_id]["password"] == hashed_password:
                    st.session_state["logged_in"] = True
                    st.session_state["current_user"] = user_id
                    st.session_state["subjects"] = st.session_state["accounts"][user_id]["subjects"]
                    st.success("Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
            else:
                st.error("User ID does not exist.")

    elif action == "Create Account":
        user_id = st.text_input("Choose a User ID")
        password = st.text_input("Choose a Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Create Account"):
            if user_id in st.session_state["accounts"]:
                st.error("User ID already exists. Please choose another.")
            elif password != confirm_password:
                st.error("Passwords do not match. Please try again.")
            else:
                st.session_state["accounts"][user_id] = {
                    "password": hash_password(password),
                    "subjects": {},
                }
                st.success("Account created successfully! You can now log in.")

def study_timer():
    st.title("StudySync")

    # Input Section for adding subjects
    st.sidebar.header("Manage Subjects")
    category = st.sidebar.text_input("Enter Category:")
    subject = st.sidebar.text_input("Enter Subject:")
    add_subject = st.sidebar.button("Add Subject")
    if add_subject:
        if category and subject:
            if category not in st.session_state["subjects"]:
                st.session_state["subjects"][category] = {}
            if subject not in st.session_state["subjects"][category]:
                st.session_state["subjects"][category][subject] = 0.0
                st.session_state["message"] = f"Added subject '{subject}' under category '{category}'."
            else:
                st.session_state["message"] = f"Subject '{subject}' already exists under category '{category}'."
        else:
            st.session_state["message"] = "Please enter both category and subject."

    # Delete Subject Option in Sidebar
    if st.session_state["subjects"]:
        st.sidebar.subheader("🗑️ Delete Subject")
        selected_category_for_delete = st.sidebar.selectbox(
            "Choose Category", options=["Select"] + list(st.session_state["subjects"].keys()), key="delete_category"
        )
        if selected_category_for_delete != "Select":
            subjects_in_category = list(st.session_state["subjects"][selected_category_for_delete].keys())
            selected_subject_for_delete = st.sidebar.selectbox(
                "Choose Subject", options=["Select"] + subjects_in_category, key="delete_subject"
            )
            if selected_subject_for_delete != "Select":
                delete_subject = st.sidebar.button("Delete Selected Subject")
                if delete_subject:
                    del st.session_state["subjects"][selected_category_for_delete][selected_subject_for_delete]
                    st.success(f"Deleted subject '{selected_subject_for_delete}' under category '{selected_category_for_delete}'.")
                    if not st.session_state["subjects"][selected_category_for_delete]:
                        del st.session_state["subjects"][selected_category_for_delete]  # Remove category if empty
                    st.rerun()

    if st.session_state["message"]:
        st.sidebar.success(st.session_state["message"])
        st.session_state["message"] = ""

    # Choose Category and Subjects
    st.header("📚 Select a Subject")
    categories = list(st.session_state["subjects"].keys())
    if categories:
        selected_category = st.selectbox("Choose a Category", options=["Select"] + categories)
        if selected_category != "Select":
            subjects = list(st.session_state["subjects"][selected_category].keys())
            selected_subject = st.selectbox("Choose a Subject", options=["Select"] + subjects)
            if selected_subject != "Select":
                st.subheader(f"🕒 Study Timer for {selected_subject} under {selected_category}")

                # Start/Stop studying logic
                if not st.session_state["studying"]:
                    start_button = st.button("Start Studying", key="start_button")
                    if start_button:
                        st.session_state["studying"] = True
                        st.session_state["start_time"] = time.time()
                        st.success("Study session started!")
                        st.rerun()

                if st.session_state["studying"]:
                    st.info("🟢 Study session in progress")
                    stop_button = st.button("Stop Studying", key="stop_button")
                    if stop_button:
                        elapsed_time = time.time() - st.session_state["start_time"]
                        st.session_state["subjects"][selected_category][selected_subject] += elapsed_time
                        st.session_state["studying"] = False
                        st.session_state["start_time"] = None
                        st.success(f"You studied for {format_time(elapsed_time)}.")
                        st.rerun()
    else:
        st.write("No categories or subjects added yet. Use the sidebar to add them!")

    # Display total time spent table
    st.header("📊 Time Spent on Subjects")
    data = []
    for category, subjects in st.session_state["subjects"].items():
        for subject, time_spent in subjects.items():
            data.append([category, subject, format_time(time_spent)])
    if data:
        df = pd.DataFrame(data, columns=["Category", "Subject", "Time Spent"])
        st.table(df)
    else:
        st.write("No time logged yet!")

    if st.button("Logout"):
        # Save progress and logout
        st.session_state["accounts"][st.session_state["current_user"]]["subjects"] = st.session_state["subjects"]
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.rerun()


# Main Application Logic
if not st.session_state["logged_in"]:
    login_page()
else:
    study_timer()
