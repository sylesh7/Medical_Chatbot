# CURO BOT 🤖

### WHERE TECHNOLOGY MEETS CARE

CURO BOT is an AI-powered chatbot and personalized healthcare assistant that provides medical guidance, medicine information, and emergency SOS alert features. It also includes live location sharing via a Telegram bot for emergency situations.

Chatbot:
https://curobot-skt.streamlit.app/

## 🚀 Features

- **User Authentication**
  - Login & Signup with secure authentication
  - Stores user medical details (height, weight, blood group, etc.)

- **AI-Powered Chatbot**
  - Uses Gemini AI to answer medical queries
  - Maintains chat history for reference

- **Personalized Medicine Assistance**
  - Predicts diseases based on symptoms
  - Provides remedies, medications (without dosage), and alternative treatments

- **Medicine Information Lookup**
  - Fetches medicine details (composition, uses, side effects, alternatives)

- **Emergency SOS Alert System**
  - Sends SOS messages with real-time location to Telegram contacts
  - Fetches user’s location automatically using JavaScript & LocalStorage

## 📌 Setup Instructions

### 1️⃣ Clone the Repository
```sh
   git clone https://github.com/yourusername/curo-bot.git
   cd curo-bot
```

### 2️⃣ Install Dependencies
```sh
   pip install -r requirements.txt
```

### 3️⃣ Set Up Environment Variables
Create a `.env` file and add:
```sh
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_IDS=chat_id1,chat_id2,..,chat_idn
```

### 4️⃣ Run the Application
```sh
   python -m streamlit run app.py
```

## 📷 Screenshots
(Include relevant screenshots of your UI here)

## 📜 Technologies Used
- **Python** (Streamlit, Pandas, Requests)
- **Google Gemini AI** (For AI-powered responses)
- **Telegram Bot API** (For sending location and SOS alerts)
- **HTML, JavaScript** (For location fetching & user interaction)

## 🔗 API Usage
- **Google Gemini AI API** for medical chatbot responses
- **Telegram API** for location & emergency alerts

## 🤝 Contributing
Contributions are welcome! Fork this repository, make your changes, and submit a pull request.

## 📄 License
This project is licensed under the **MIT License**.

---

### 💡 Developer Notes
If you face any issues with location fetching, ensure:
1. **Browser permissions** allow location access.
2. **JavaScript execution** is enabled.
3. **Your Telegram bot is correctly set up** to receive messages.

📧 Contact: sylesh.27it@licet.ac.in

