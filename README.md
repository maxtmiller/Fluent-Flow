
# `FluentFlow`

![Python](https://img.shields.io/badge/Python-3776AB?style=flat\&logo=python\&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat\&logo=flask\&logoColor=white) ![FFmpeg](https://img.shields.io/badge/FFmpeg-000000?style=flat\&logo=ffmpeg\&logoColor=white)

**Interactive language-learning platform for expats — improve speaking and integrate seamlessly in the workplace.**

---

## Preview

<img width="1400" height="775" alt="fluentflow_cover" src="https://github.com/user-attachments/assets/e4e33aa6-39bc-4306-9c61-ebeecb95c861" />

---

## Features

* Interactive AI-powered conversation practice
* Dynamic feedback and sentence construction guidance
* Stores transcripts and session data for personalized learning
* User-friendly interface with secure Google OAuth login

---

## Tech Stack

* **Backend:** Python, Flask
* **AI Integration:** ChatGPT API for dynamic conversations and text-to-speech
* **Data Storage:** Local databases for transcripts and session tracking
* **Media Handling:** FFmpeg for audio processing

---

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/maxtmiller/FluentFlow.git
   cd FluentFlow
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables (ChatGPT API key, OAuth credentials)
4. Run the Flask server:

   ```bash
   flask run
   ```
5. Open your browser at `http://localhost:5000`

---

## Next Steps

* Add support for multiple languages and accents
* Implement progress analytics and conversation scoring
* Integrate real-time audio streaming for live practice sessions
