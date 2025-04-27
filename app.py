import streamlit as st
import google.generativeai as genai
import pandas as pd
import requests
import os
import telebot
import geocoder

# ✅ Correct import
# ❌ Don't import configure/generate_content separately

if "name" not in st.session_state:
    st.session_state.name = ""  
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  
if "location" not in st.session_state:
    st.session_state.location = None  

# ✅ First check API Key
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("❌ API Key not found. Set GEMINI_API_KEY as an environment variable.")
    st.stop()

# ✅ Configure after checking
genai.configure(api_key=API_KEY)

# ✅ Create model instance
model = genai.GenerativeModel(model_name="gemini-1.5-pro")  


def get_gemini_response(input_text):
    try:
        response = model.generate_content(input_text)

        if not response or not response.candidates or not response.candidates[0].content.parts:
            return "⚠️ No valid response from the AI. Try rephrasing your request."

        response_text = response.candidates[0].content.parts[0].text
        return response_text

    except Exception as e:
        return f"⚠️ An error occurred: {str(e)}"


def authenticate_user(username, password):
    user_data = pd.read_csv("users.csv")
    if username in user_data["user_id"].values:
        stored_password = user_data.loc[user_data["user_id"] == username, "passwords"].values[0]
        if password == stored_password:
            st.success("✅ Login successful!")
            st.session_state.name = username
        else:
            st.error("❌ Incorrect password. Please try again.")
    else:
        st.error("❌ Username not found. Please create a new account.")


def create_new_account(new_userid, username, password, email, dob, height, weight, gender, blood_group):
    user_data = pd.read_csv("users.csv")
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


def chat_page():
    st.markdown("<h1 style='text-align: center; color:#28b463;'>CURO BOT🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color:#28b463;'>WHERE TECHNOLOGY MEETS CARE</h5>", unsafe_allow_html=True)
    chat = st.chat_input("Say something...")

    if chat:
        st.session_state.chat_history.append(chat)
        with st.chat_message("user"):
            st.write(chat)
        with st.chat_message("assistant"):
            response = get_gemini_response(chat)
            st.write(response)


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


def predictor():
    st.title("Medicine Information 📜")
    medicine_name = st.text_input("Enter the name of the medicine")

    if medicine_name:
        prompt = f"Provide general information about '{medicine_name}'. Include composition, uses, side effects, and alternatives in a table format."
        response = get_gemini_response(prompt)
        st.write(response)


def emergency_sos():
    st.title("🚨 SOS Alert System")
    st.write("Send an emergency alert via Telegram bot with live location.")

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(",")

    if not TELEGRAM_BOT_TOKEN or not CHAT_IDS:
        st.error("❌ Telegram Bot credentials are missing. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_IDS.")
        return

    name = st.text_input("Enter your name:", key="sos_name")
    message = st.text_area("Enter your SOS message:", key="sos_message")

    def get_live_location():
        g = geocoder.ip('me')
        if g.latlng:
            return g.latlng
        return None

    def send_sos_telegram(user_name, message):
        location = get_live_location()
        full_message = f"🚨 Emergency Alert!\n{user_name} needs urgent help!\n\n📩 Message: {message}"

        if location:
            full_message += f"\n\n📍 Live Location: {location[0]}, {location[1]}"

        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

        for chat_id in CHAT_IDS:
            chat_id = chat_id.strip()
            try:
                bot.send_message(chat_id, full_message)
                if location:
                    bot.send_location(chat_id, latitude=location[0], longitude=location[1])
                st.success(f"✅ SOS Alert sent successfully to ")
            except Exception as e:
                st.error(f"❌ Failed to send SOS Alert : {e}")

    if st.button("Send SOS Message"):
        if name and message:
            send_sos_telegram(name, message)
        else:
            st.warning("⚠️ Please fill in all fields.")


# Sidebar Navigation
with st.sidebar:
    st.title("Curo Bot")
    pages_select = st.selectbox("Navigation", ["Login", "Chatbot", "Personalised Medicine", "Medicine Info", "Emergency SOS"])

    st.header("Chat History")
    for msg in st.session_state['chat_history']:
        st.write(f"{msg}")

# Main Pages
if pages_select == "Login":
    main()
elif pages_select == "Chatbot":
    chat_page()
elif pages_select == "Personalised Medicine":
    med()
elif pages_select == "Medicine Info":
    predictor()
elif pages_select == "Emergency SOS":
    emergency_sos()
