# import streamlit as st
# import pandas as pd
# import os
# import cv2
# import mediapipe as mp
# from datetime import datetime, timedelta
# import random
# import firebase_admin
# from firebase_admin import credentials, firestore

# # Load Firebase credentials from Streamlit's secrets
# firebase_creds = {
#     "type": "service_account",
#     "project_id": st.secrets["firebase_project_id"],
#     "private_key_id": st.secrets["firebase_private_key_id"],
#     "private_key": st.secrets["firebase_private_key"].replace('\\n', '\n'),  # Handle multiline private key
#     "client_email": st.secrets["firebase_client_email"],
#     "client_id": st.secrets["firebase_client_id"],
#     "auth_uri": st.secrets["firebase_auth_uri"],
#     "token_uri": st.secrets["firebase_token_uri"],
#     "auth_provider_x509_cert_url": st.secrets["firebase_auth_provider_x509_cert_url"],
#     "client_x509_cert_url": st.secrets["firebase_client_x509_cert_url"]
# }

# # Firebase Initialization
# if not firebase_admin._apps:
#     try:
#         cred = credentials.Certificate(firebase_creds)
#         firebase_admin.initialize_app(cred)
#         db = firestore.client()
#         st.success("Firebase initialized successfully!")
#     except Exception as e:
#         st.error(f"Error initializing Firebase: {e}")
#         raise e  # Stop execution if Firebase setup fails

# # MediaPipe Pose Detection Setup
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=True)
# mp_drawing = mp.solutions.drawing_utils

# # Define helper functions
# def handle_sign_up_login(username, password):
#     """Function to handle user sign up or login."""
#     if not username or not password:
#         return "Please provide both username and password", None
#     try:
#         # Check if the user exists
#         user_ref = db.collection("users").document(username)
#         doc = user_ref.get()
#         if doc.exists:
#             # Existing user, check password
#             user_data = doc.to_dict()
#             if user_data["password"] == password:
#                 return "Logged in successfully!", user_data
#             else:
#                 return "Incorrect password", None
#         else:
#             # New user, create an account
#             user_ref.set({
#                 "username": username,
#                 "password": password,
#                 "created_at": datetime.now()
#             })
#             return "Account created successfully!", None
#     except Exception as e:
#         return f"Error: {e}", None

# def generate_fitness_tasks(username, age, fitness_level):
#     """Generate fitness tasks based on user details."""
#     if not age.isdigit() or not (7 <= int(age) <= 14):
#         return "Age must be between 7 and 14.", None
#     task_list = {
#         "beginner": ["Jumping Jacks", "Squats", "Push-Ups"],
#         "intermediate": ["Burpees", "Mountain Climbers", "Lunges"],
#         "advanced": ["Sprints", "Plank", "Pull-Ups"]
#     }
#     task = random.choice(task_list[fitness_level])
#     try:
#         task_ref = db.collection("tasks").document(username)
#         task_ref.set({
#             "age": age,
#             "fitness_level": fitness_level,
#             "task": task,
#             "created_at": datetime.now()
#         })
#         return f"Fitness task generated for {username}", task
#     except Exception as e:
#         return f"Error generating task: {e}", None

# def submit_proof(username, task_name, proof_file):
#     """Submit proof of task completion."""
#     try:
#         file_path = f"proofs/{username}_{task_name}_{proof_file.name}"
#         with open(file_path, "wb") as f:
#             f.write(proof_file.read())
#         # Optionally, save proof data to Firebase
#         db.collection("proofs").add({
#             "username": username,
#             "task_name": task_name,
#             "proof_path": file_path,
#             "submitted_at": datetime.now()
#         })
#         return f"Proof for {task_name} submitted successfully!"
#     except Exception as e:
#         return f"Error submitting proof: {e}"

# def view_activity_log(username):
#     """View user activity log."""
#     try:
#         task_ref = db.collection("tasks").document(username)
#         doc = task_ref.get()
#         if doc.exists:
#             data = doc.to_dict()
#             log_df = pd.DataFrame([data])
#             return log_df
#         else:
#             return "No tasks found for this user."
#     except Exception as e:
#         return f"Error fetching activity log: {e}"

# # Main App Function
# def create_app():
#     # Streamlit layout
#     st.title("Fitness Challenge App with Firebase Integration")

#     # Sign Up / Login Tab
#     tab1, tab2, tab3, tab4 = st.tabs(["Sign Up / Login", "Generate Tasks", "Submit Proof", "View Activity Log"])

#     with tab1:
#         st.subheader("Sign Up / Login")
#         username_input = st.text_input("Enter Username")
#         password_input = st.text_input("Enter Password", type="password")
#         if st.button("Sign Up / Login"):
#             status, _ = handle_sign_up_login(username_input, password_input)
#             st.info(status)

#     with tab2:
#         st.subheader("Generate Tasks")
#         username_gen = st.text_input("Enter Username (For Task Generation)")
#         age = st.text_input("Enter Age (7-14)")
#         fitness_level = st.radio("Select Fitness Level", ["beginner", "intermediate", "advanced"])
#         if st.button("Generate Tasks"):
#             task_output, task_display = generate_fitness_tasks(username_gen, age, fitness_level)
#             st.info(task_output)
#             if task_display:
#                 st.success(f"Generated Task: {task_display}")

#     with tab3:
#         st.subheader("Submit Proof")
#         username_proof = st.text_input("Enter Username (For Proof Submission)")
#         task_name = st.text_input("Enter Task Name")
#         proof = st.file_uploader("Upload Image/Video Proof", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
#         if st.button("Submit Proof"):
#             if proof:
#                 result = submit_proof(username_proof, task_name, proof)
#                 st.info(result)

#     with tab4:
#         st.subheader("View Activity Log")
#         username_log = st.text_input("Enter Username (For Activity Log)")
#         if st.button("View Log"):
#             log_df = view_activity_log(username_log)
#             if isinstance(log_df, pd.DataFrame):
#                 st.dataframe(log_df)
#             else:
#                 st.error(log_df)

# if __name__ == '__main__':
#     create_app()       




import streamlit as st
import pandas as pd
import numpy as np
import cv2
import mediapipe as mp
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Page configuration
st.set_page_config(
    page_title="Fitness Challenge App",
    page_icon="💪",
    layout="wide"
)

# Initialize Firebase
@st.cache_resource
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            firebase_config = st.secrets["firebase"]
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception as e:
            st.error(f"Error initializing Firebase: {e}")
            return None

# MediaPipe setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=True)

def analyze_pose(proof_file, task):
    try:
        file_bytes = proof_file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        
        if proof_file.type.startswith('image'):
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if image is None:
                return False, "Invalid image file."
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            
            if results.pose_landmarks:
                return True, "Pose detected successfully!"
            return False, "No pose detected. Please try again."
            
        elif proof_file.type.startswith('video'):
            temp_file = f"temp_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
            with open(temp_file, 'wb') as f:
                f.write(file_bytes)
            
            cap = cv2.VideoCapture(temp_file)
            pose_detected = False
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)
                
                if results.pose_landmarks:
                    pose_detected = True
                    break
                    
            cap.release()
            os.remove(temp_file)
            
            if pose_detected:
                return True, "Pose detected in video!"
            return False, "No pose detected in video."
        
        return False, "Invalid file format."
        
    except Exception as e:
        return False, f"Error analyzing file: {e}"

def sign_up_or_login(db, username, password):
    try:
        user_doc = db.collection("users").document(username.lower()).get()
        
        if user_doc.exists:
            # Login
            stored_password = user_doc.to_dict().get("password")
            if stored_password == password:
                return True, "Login successful!"
            return False, "Incorrect password."
        else:
            # Sign up
            user_data = {
                "username": username.lower(),
                "password": password,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tasks": []
            }
            db.collection("users").document(username.lower()).set(user_data)
            return True, "Sign up successful!"
            
    except Exception as e:
        return False, f"Error: {e}"

def generate_task(db, username, age, fitness_level):
    try:
        age = int(age)
        if not (7 <= age <= 14):
            return False, "Age must be between 7 and 14."

        tasks = {
            (7, 10): {
                "beginner": {"task": "Jumping Jacks", "details": "10 reps"},
                "intermediate": {"task": "Push-ups", "details": "10 reps"},
                "advanced": {"task": "Squats", "details": "10 reps"}
            },
            (11, 12): {
                "beginner": {"task": "Jumping Jacks", "details": "15 reps"},
                "intermediate": {"task": "Push-ups", "details": "15 reps"},
                "advanced": {"task": "Squats", "details": "15 reps"}
            },
            (13, 14): {
                "beginner": {"task": "Jumping Jacks", "details": "20 reps"},
                "intermediate": {"task": "Push-ups", "details": "20 reps"},
                "advanced": {"task": "Squats", "details": "20 reps"}
            }
        }

        for age_range, level_tasks in tasks.items():
            if age_range[0] <= age <= age_range[1]:
                if fitness_level in level_tasks:
                    task = level_tasks[fitness_level]
                    task_data = {
                        "task": task["task"],
                        "details": task["details"],
                        "status": "pending",
                        "assigned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "completed_at": None,
                        "proof_uploaded": False
                    }
                    
                    # Add task to user's tasks
                    user_ref = db.collection("users").document(username.lower())
                    user_doc = user_ref.get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        tasks = user_data.get("tasks", [])
                        tasks.append(task_data)
                        user_ref.update({"tasks": tasks})
                        return True, f"Task assigned: {task['task']} - {task['details']}"
                    
                    return False, "User not found."
                    
        return False, "Invalid age range or fitness level."
        
    except Exception as e:
        return False, f"Error generating task: {e}"

def main():
    db = initialize_firebase()
    if not db:
        st.error("Failed to initialize Firebase.")
        return

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Sign Up / Login", "Generate Tasks", "Submit Proof", "Progress Tracker"])

    if page == "Sign Up / Login":
        st.title("Sign Up / Login")
        
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username")
        with col2:
            password = st.text_input("Password", type="password")
            
        if st.button("Submit"):
            if username and password:
                success, message = sign_up_or_login(db, username, password)
                if success:
                    st.success(message)
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password.")

    elif page == "Generate Tasks":
        st.title("Generate New Task")
        
        username = st.text_input("Username")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=7, max_value=14, value=7)
        with col2:
            fitness_level = st.selectbox("Fitness Level", ["beginner", "intermediate", "advanced"])
            
        if st.button("Generate Task"):
            if username:
                success, message = generate_task(db, username, age, fitness_level)
                if success:
                    st.success(message)
                else:
                    st.error(message)
            else:
                st.warning("Please enter a username.")

    elif page == "Submit Proof":
        st.title("Submit Task Proof")
        
        username = st.text_input("Username")
        task = st.text_input("Task Name")
        proof_file = st.file_uploader("Upload Proof (Image/Video)", type=["jpg", "jpeg", "png", "mp4", "mov"])
        
        if st.button("Submit"):
            if username and task and proof_file:
                success, message = analyze_pose(proof_file, task)
                if success:
                    # Update task status in Firebase
                    user_ref = db.collection("users").document(username.lower())
                    user_doc = user_ref.get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        tasks = user_data.get("tasks", [])
                        
                        task_updated = False
                        for t in tasks:
                            if t["task"] == task and t["status"] == "pending":
                                t["status"] = "completed"
                                t["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                t["proof_uploaded"] = True
                                task_updated = True
                                break
                                
                        if task_updated:
                            user_ref.update({"tasks": tasks})
                            st.success("Task completed successfully!")
                        else:
                            st.error("Task not found or already completed.")
                    else:
                        st.error("User not found.")
                else:
                    st.error(message)
            else:
                st.warning("Please fill in all fields and upload a proof file.")

    elif page == "Progress Tracker":
        st.title("Progress Tracker")
        
        username = st.text_input("Username")
        
        if st.button("View Progress"):
            if username:
                user_doc = db.collection("users").document(username.lower()).get()
                
                if user_doc.exists:
                    user_data = user_doc.to_dict()
                    tasks = user_data.get("tasks", [])
                    
                    if tasks:
                        df = pd.DataFrame(tasks)
                        st.dataframe(df)
                        
                        # Statistics
                        completed_tasks = len([t for t in tasks if t["status"] == "completed"])
                        pending_tasks = len([t for t in tasks if t["status"] == "pending"])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Completed Tasks", completed_tasks)
                        with col2:
                            st.metric("Pending Tasks", pending_tasks)
                    else:
                        st.info("No tasks found.")
                else:
                    st.error("User not found.")
            else:
                st.warning("Please enter a username.")

if __name__ == "__main__":
    main()
