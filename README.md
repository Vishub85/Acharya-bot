# 🤖 Acharya Bot

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Vishub85/Acharya-bot)

An intelligent chatbot helper for **Acharya ERP Tech** that provides instant and automated answers about admissions, courses, placements, hostel facilities, campus events, and general campus inquiries. 

The chatbot utilizes real-time web scraping to extract accurate details from the official site and falls back to cached data and **Groq LLM** generation when live services are unavailable.

---

## 🛠️ Features

- **Live Website Scraping**: Automatically extracts admissions, placements, and course listings from the official site using BeautifulSoup.
- **Smart LLM Generation**: Falls back to Groq AI inference when user queries are complex or off-topic.
- **Local Cache**: Features a 12-hour automated caching mechanism to minimize external network requests and ensure fast responses.
- **Interactive Application Form**: Includes an `/apply` admission form page that records user responses to `submissions.json`.
- **Responsive Web Interface**: Sleek, responsive chat layout styled with vanilla CSS.

---

## 💻 Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **HTML Parsing & Extraction**: BeautifulSoup4, Requests
- **Generative AI**: Groq API
- **Frontend**: HTML5, CSS3, Vanilla JavaScript

---

## 🚀 One-Click Cloud Deployment

To deploy this project to the cloud instantly as a Render Blueprint Project:

1. Click the **Deploy to Render** button at the top of this page.
2. Enter your **`GROQ_API_KEY`** when prompted.
3. Click **Apply** or **Create Web Service**. 
4. Render will use the pre-configured [render.yaml](render.yaml) file to build, run, and manage your services as a project.

---

## 📦 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Vishub85/Acharya-bot.git
   cd Acharya-bot
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your API keys:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=groq-1
   GROQ_API_URL=https://api.groq.ai/v1/models/groq-1/infer
   ```

5. **Run the development server:**
   ```bash
   python app.py
   ```
   Open `http://127.0.0.1:5000` in your web browser.

---

## 📂 Project Structure

```text
├── static/
│   ├── acharya_data.json  # Cached scraping data
│   ├── acharya_logo.svg   # Brand assets
│   ├── script.js          # Chatbot logic and messaging UI
│   └── style.css          # Core styles
├── templates/
│   ├── apply.html         # Application form template
│   └── index.html         # Main chatbot chat template
├── .gitignore             # Excluded files (virtual environments, keys)
├── app.py                 # Flask server routes
├── render.yaml            # Render Blueprint Infrastructure-as-code
├── requirements.txt       # Production dependencies
├── responses.py           # Scraping, caching, and Groq inference engine
└── run.bat                # Local Windows startup batch script
```
