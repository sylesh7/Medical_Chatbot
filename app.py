import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# Initialize session state variables
if "name" not in st.session_state:
    st.session_state.name = ""  # Stores logged-in username
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores chat messages

# Set API key using environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API Key not found. Set GEMINI_API_KEY as an environment variable.")
    st.stop()

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Load user data
user_data = pd.read_csv("users.csv")

# Function to get Gemini AI response with error handling
def get_gemini_response(input_text):
    try:
        response = model.generate_content(input_text)
        
        if not response or not response.candidates or not response.candidates[0].content.parts:
            return "⚠️ No valid response from the AI. Try rephrasing your request."
        
        response_text = response.candidates[0].content.parts[0].text
        return response_text

    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"

# Authentication function
def authenticate_user(username, password):
    if username in user_data["user_id"].values:
        stored_password = user_data.loc[user_data["user_id"] == username, "passwords"].values[0]
        if password == stored_password:
            st.success("✅ Login successful!")
            st.session_state.name = username
        else:
            st.error("❌ Incorrect password. Please try again.")
    else:
        st.error("❌ Username not found. Please create a new account.")

# Function to create new account (DOB without restrictions)
def create_new_account(new_userid, username, password, email, dob, height, weight, gender, blood_group):
    if len(password) < 8:
        st.warning("⚠️ Password must be at least 8 characters long.")
        return

    if username in user_data["user_name"].values:
        st.error("❌ Username already exists. Choose a different username.")
        return

    new_account = pd.DataFrame({
        "user_id": [new_userid], "user_name": [username], "passwords": [password],
        "email": [email], "dob": [dob], "height": [height], "weight": [weight],
        "gender": [gender], "blood_group": [blood_group]
    })
    user_data_updated = pd.concat([user_data, new_account], ignore_index=True)
    user_data_updated.to_csv("users.csv", index=False)
    st.success("✅ Account created successfully!")

# Main login/signup page
def main():
    st.title(":blue[Login]") 
    with st.form(key="login_form"):
        userid = st.text_input("User Id:")
        password = st.text_input("Enter password:", type="password")
        submit_button = st.form_submit_button("Login")
        if submit_button:
            authenticate_user(userid, password)

    with st.form(key="signup_form"):
        new_userid = st.text_input("Enter new user ID")
        name = st.text_input("Enter your name")
        email = st.text_input("Enter your email")
        new_password = st.text_input("New Password:", type="password")
        dob = st.date_input("Enter your date of birth", min_value=pd.to_datetime("1900-01-01"), max_value=pd.to_datetime("today"))
        height = st.number_input("Enter height (cm):", 0, 350)
        weight = st.number_input("Enter weight (kg):", 0, 200)
        gender = st.radio("Select gender:", ["Male", "Female", "Other"])
        blood_group = st.selectbox("Select your blood group:", ["A+", "B+", "A-", "B-", "O+", "O-", "AB+", "AB-"]) 
        create_account_button = st.form_submit_button("Create Account")

        if create_account_button:
            create_new_account(new_userid, name, new_password, email, dob, height, weight, gender, blood_group)

# Sidebar navigation
with st.sidebar:
    st.title("MedInnovate")
    pages_select = st.selectbox("Navigation", ["Login", "Chatbot", "Personalised Medicine", "Medicine Info"])

    st.header("Chat History")
    for msg in st.session_state['chat_history']:
        st.write(f"{msg}")

# Page Routing
if pages_select == "Login":
    main()
