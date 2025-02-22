import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import os
from streamlit.components.v1 import html

# Initialize session state variables
if "name" not in st.session_state:
    st.session_state.name = ""  # Stores logged-in username
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores chat messages
if "location" not in st.session_state:
    st.session_state.location = None  # Stores user's location

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

# Chatbot Page
def chat_page():
    st.markdown("<h1 style='text-align: center; color:#28b463;'>CURO BOT🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color:#28b463;'>WHERE TECHNOLOGY MEETS CARE</h1>", unsafe_allow_html=True)
    chat = st.chat_input("Say something...")

    if chat:
        st.session_state.chat_history.append(chat)
        with st.chat_message("user"):
            st.write(chat)
        with st.chat_message("assistant"):
            response = get_gemini_response(chat)
            st.write(response)

# Personalised Medicine Page
def med():
    st.title("Personalised Medicine 🏥")
    symptom = st.text_input("Enter your symptom")
    days = st.text_input("For how many days?")
    other_symptoms = st.text_input("Other symptoms")
    other_diseases = st.text_input("Do you have any other diseases?")

    if symptom:
        question_prompt = f"Generate a question to better understand the disease based on symptom={symptom}, days={days}, other symptoms={other_symptoms}"
        question = get_gemini_response(question_prompt)

        answer = st.text_input(question)
       
        diagnosis_prompt = (
            f"Predict the disease based on symptoms: {symptom}, duration: {days}, other symptoms: {other_symptoms}, answer to previous question: {answer}, "
            f"and existing diseases: {other_diseases}. Provide remedies, medication (without dosage), and alternative treatments."
        )
       
        response = get_gemini_response(diagnosis_prompt)
        st.write(response)

# Medicine Information Predictor
def predictor():
    st.title("Medicine Information 📜")
    medicine_name = st.text_input("Enter the name of the medicine")

    if medicine_name:
        prompt = f"Provide general information about '{medicine_name}'. Include composition, uses, side effects, and alternatives in a table format."
        response = get_gemini_response(prompt)
        st.write(response)

# Sidebar Navigation
with st.sidebar:
    st.title("Curo Bot")
    pages_select = st.selectbox("Navigation", ["Login", "Chatbot", "Personalised Medicine", "Medicine Info", "Emergency SOS"])

    st.header("Chat History")
    for msg in st.session_state['chat_history']:
        st.write(f"{msg}")

# Page Routing
if pages_select == "Login":
    main()
elif pages_select == "Chatbot":
    chat_page()
elif pages_select == "Personalised Medicine":
    med()
elif pages_select == "Medicine Info":
    predictor()

# Get Bot Token and Chat IDs from Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

# Function to send SOS alert with location
def send_sos_telegram(user_name, location=None):
    if not TELEGRAM_BOT_TOKEN or not CHAT_IDS:
        st.error("❌ Telegram Bot credentials missing. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS.")
        return

    message = f"🚨 Emergency Alert! {user_name} is in a critical health condition. Please check on them immediately."
    if location:
        message += f"\n\n📍 Location: {location}"

    for chat_id in CHAT_IDS:
        chat_id = chat_id.strip()
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            st.success(f"✅ SOS Alert sent successfully to {chat_id}")
        else:
            st.error(f"❌ Failed to send SOS Alert to {chat_id}: {response.json()}")

# Emergency SOS Page
if pages_select == "Emergency SOS":
    st.title("🚑 Emergency SOS Alert System")
    
    user_name = st.text_input("Enter your name:")
    
    # Requesting geolocation from the user using JavaScript
    html("""
        <script>
        function getLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(showPosition);
            } else { 
                document.getElementById("location").value = "Geolocation is not supported by this browser.";
            }
        }

        function showPosition(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            console.log(latitude)
            const location = `${latitude},${longitude}`;
            localStorage.setItem("location",location)
            document.getElementById("location_button").style.display = 'none';
        }
        console.log(latitude)
        </script>
        <button id="location_button" onclick="getLocation()">📍 Get Location</button>
    """)

    location = st.text_input("Your location (auto-filled)", key="location")

    if st.button("🚨 Send Telegram SOS Alert"):
        if user_name:
            send_sos_telegram(user_name, location)
        else:
            st.warning("⚠️ Please enter your name.")
