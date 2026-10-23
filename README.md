# Student Quiz AI

A beginner-friendly AI quiz generator built with Python, Streamlit, and the Google Gemini API.

## Features

- Choose a subject, topic, and difficulty.
- Generate 3–10 multiple-choice questions.
- Answer the questions and see your score.
- Review the correct answers and explanations.

## 1. Get a Gemini API key

Create a key at https://aistudio.google.com/api-keys. Check Google's current Gemini API pricing and free-tier limits at https://ai.google.dev/gemini-api/docs/pricing.

**Keep your API key private. Never commit it to GitHub.**

## 2. Run it on your computer

Install Python 3.10 or newer, then open a terminal in this project folder.

Create and activate a virtual environment (optional but recommended):

### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a folder called `.streamlit` if it does not already exist. Inside it, create a file named `secrets.toml` with this content:

```toml
GEMINI_API_KEY = "paste-your-real-api-key-here"
```

Replace the example value with your actual key. Do not share or upload this file.

Run the app:

```powershell
python -m streamlit run app.py
```

Streamlit will show a local web address, usually http://localhost:8501. Open it in your browser.

## 3. Upload to GitHub

1. Sign in to https://github.com and create a new repository.
2. Upload `app.py`, `requirements.txt`, `README.md`, and `.gitignore`.
3. Do **not** upload `.streamlit/secrets.toml`. The `.gitignore` file helps prevent this.
4. If you use GitHub's website to upload files, upload the contents of this project folder, not the ZIP file itself.

## 4. Deploy online with Streamlit Community Cloud

1. Open https://share.streamlit.io/ and sign in with GitHub.
2. Create a new app and select your repository and `app.py`.
3. In the app settings, open **Secrets** and add:

```toml
GEMINI_API_KEY = "paste-your-real-api-key-here"
```

4. Save and deploy. Wait for the app to build.

Free availability, model access, and usage limits can change. If the app reports a model or quota error, check Google's current Gemini API documentation and available models.

## Troubleshooting

- **Missing API key:** Check the local `.streamlit/secrets.toml` file or Streamlit Cloud Secrets.
- **Invalid API key:** Create or copy a fresh key in Google AI Studio.
- **Quota / 429 error:** You may have reached a usage limit; wait and check your account's current limits.
- **Installation error:** Confirm Python is installed, then rerun `python -m pip install -r requirements.txt`.

## Project note

This is a prototype for learning and demonstration. AI-generated content can contain mistakes, so verify important answers using reliable learning materials.
