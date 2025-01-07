import streamlit as st
import pandas as pd
import os
import cv2
import mediapipe as mp
from datetime import datetime, timedelta
import random
import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials from Streamlit's secrets
firebase_creds = {
    "type": "service_account",
    "project_id": st.secrets["firebase_project_id"],
    "private_key_id": st.secrets["firebase_private_key_id"],
    "private_key": st.secrets["firebase_private_key"].replace('\\n', '\n'),  # Handle multiline private key
    "client_email": st.secrets["firebase_client_email"],
    "client_id": st.secrets["firebase_client_id"],
    "auth_uri": st.secrets["firebase_auth_uri"],
    "token_uri": st.secrets["firebase_token_uri"],
    "auth_provider_x509_cert_url": st.secrets["firebase_auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["firebase_client_x509_cert_url"]
}

# Firebase Initialization
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        st.success("Firebase initialized successfully!")
    except Exception as e:
        st.error(f"Error initializing Firebase: {e}")
        raise e  # Stop execution if Firebase setup fails

# MediaPipe Pose Detection Setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=True)
mp_drawing = mp.solutions.drawing_utils

# Define helper functions
def handle_sign_up_login(username, password):
    """Function to handle user sign up or login."""
    if not username or not password:
        return "Please provide both username and password", None
    try:
        # Check if the user exists
        user_ref = db.collection("users").document(username)
        doc = user_ref.get()
        if doc.exists:
            # Existing user, check password
            user_data = doc.to_dict()
            if user_data["password"] == password:
                return "Logged in successfully!", user_data
            else:
                return "Incorrect password", None
        else:
            # New user, create an account
            user_ref.set({
                "username": username,
                "password": password,
                "created_at": datetime.now()
            })
            return "Account created successfully!", None
    except Exception as e:
        return f"Error: {e}", None

def generate_fitness_tasks(username, age, fitness_level):
    """Generate fitness tasks based on user details."""
    if not age.isdigit() or not (7 <= int(age) <= 14):
        return "Age must be between 7 and 14.", None
    task_list = {
        "beginner": ["Jumping Jacks", "Squats", "Push-Ups"],
        "intermediate": ["Burpees", "Mountain Climbers", "Lunges"],
        "advanced": ["Sprints", "Plank", "Pull-Ups"]
    }
    task = random.choice(task_list[fitness_level])
    try:
        task_ref = db.collection("tasks").document(username)
        task_ref.set({
            "age": age,
            "fitness_level": fitness_level,
            "task": task,
            "created_at": datetime.now()
        })
        return f"Fitness task generated for {username}", task
    except Exception as e:
        return f"Error generating task: {e}", None

def submit_proof(username, task_name, proof_file):
    """Submit proof of task completion."""
    try:
        file_path = f"proofs/{username}_{task_name}_{proof_file.name}"
        with open(file_path, "wb") as f:
            f.write(proof_file.read())
        # Optionally, save proof data to Firebase
        db.collection("proofs").add({
            "username": username,
            "task_name": task_name,
            "proof_path": file_path,
            "submitted_at": datetime.now()
        })
        return f"Proof for {task_name} submitted successfully!"
    except Exception as e:
        return f"Error submitting proof: {e}"

def view_activity_log(username):
    """View user activity log."""
    try:
        task_ref = db.collection("tasks").document(username)
        doc = task_ref.get()
        if doc.exists:
            data = doc.to_dict()
            log_df = pd.DataFrame([data])
            return log_df
        else:
            return "No tasks found for this user."
    except Exception as e:
        return f"Error fetching activity log: {e}"

# Main App Function
def create_app():
    # Streamlit layout
    st.title("Fitness Challenge App with Firebase Integration")

    # Sign Up / Login Tab
    tab1, tab2, tab3, tab4 = st.tabs(["Sign Up / Login", "Generate Tasks", "Submit Proof", "View Activity Log"])

    with tab1:
        st.subheader("Sign Up / Login")
        username_input = st.text_input("Enter Username")
        password_input = st.text_input("Enter Password", type="password")
        if st.button("Sign Up / Login"):
            status, _ = handle_sign_up_login(username_input, password_input)
            st.info(status)

    with tab2:
        st.subheader("Generate Tasks")
        username_gen = st.text_input("Enter Username (For Task Generation)")
        age = st.text_input("Enter Age (7-14)")
        fitness_level = st.radio("Select Fitness Level", ["beginner", "intermediate", "advanced"])
        if st.button("Generate Tasks"):
            task_output, task_display = generate_fitness_tasks(username_gen, age, fitness_level)
            st.info(task_output)
            if task_display:
                st.success(f"Generated Task: {task_display}")

    with tab3:
        st.subheader("Submit Proof")
        username_proof = st.text_input("Enter Username (For Proof Submission)")
        task_name = st.text_input("Enter Task Name")
        proof = st.file_uploader("Upload Image/Video Proof", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
        if st.button("Submit Proof"):
            if proof:
                result = submit_proof(username_proof, task_name, proof)
                st.info(result)

    with tab4:
        st.subheader("View Activity Log")
        username_log = st.text_input("Enter Username (For Activity Log)")
        if st.button("View Log"):
            log_df = view_activity_log(username_log)
            if isinstance(log_df, pd.DataFrame):
                st.dataframe(log_df)
            else:
                st.error(log_df)

if __name__ == '__main__':
    create_app()
