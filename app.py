import json
import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="Student Quiz AI",
    page_icon="📚",
    layout="centered",
)

st.markdown("""
<style>
    .main {max-width: 900px; padding-top: 2rem;}
    .hero {
        padding: 1.5rem; border-radius: 18px;
        background: linear-gradient(120deg, #e8f2ff, #f4edff);
        color: #172554; margin-bottom: 1.2rem;
    }
    .hero h1 {margin-bottom: .3rem;}
    .small-note {color: #64748b; font-size: .9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>📚 Student Quiz AI</h1>
  <p>Choose a topic, generate practice questions, and test what you know.</p>
</div>
""", unsafe_allow_html=True)

def get_api_key():
    """Read the API key from Streamlit secrets or an environment variable."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")

def generate_quiz(topic, subject, level, count):
    api_key = get_api_key()
    if not api_key:
        raise ValueError(
            "The Gemini API key is missing. Add GEMINI_API_KEY to "
            "your local .streamlit/secrets.toml file or your Streamlit "
            "Cloud app's Secrets settings."
        )

    client = genai.Client(api_key=api_key)

    schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "questions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "question": {"type": "STRING"},
                        "options": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"}
                        },
                        "answer": {"type": "STRING"},
                        "explanation": {"type": "STRING"}
                    },
                    "required": ["question", "options", "answer", "explanation"]
                }
            }
        },
        "required": ["title", "questions"]
    }

    prompt = f"""
Create exactly {count} original multiple-choice practice questions.
Subject: {subject}
Topic: {topic}
Difficulty: {level}

Requirements:
- Each question must have exactly four options.
- The answer must exactly match one of the four options.
- Include a short explanation of why the answer is correct.
- Keep questions appropriate for a student studying this subject.
- Do not include questions that depend on information not supplied in the question.
- Return only data matching the required JSON structure.
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.7,
            max_output_tokens=5000,
        ),
    )

    if not response.text:
        raise RuntimeError("The AI returned an empty response. Please try again.")
    data = json.loads(response.text)
    questions = data.get("questions", [])
    if not questions:
        raise RuntimeError("The AI did not return any questions. Please try again.")
    return data

with st.form("quiz_form"):
    left, right = st.columns(2)
    with left:
        subject = st.selectbox(
            "Subject",
            ["Mathematics", "Physics", "Chemistry", "Biology",
             "Computer Studies", "English", "General Knowledge", "Other"],
        )
        level = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
    with right:
        count = st.slider("Number of questions", min_value=3, max_value=10, value=5)
        topic = st.text_input(
            "Topic",
            placeholder="e.g. Newton's laws, fractions, HTML basics",
        )
    submitted = st.form_submit_button("✨ Generate my quiz", use_container_width=True)

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Creating your questions..."):
            try:
                st.session_state["quiz_data"] = generate_quiz(
                    topic.strip(), subject, level, count
                )
                st.session_state["quiz_topic"] = topic.strip()
                st.session_state["quiz_level"] = level
                st.session_state["answers"] = {}
            except Exception as exc:
                message = str(exc)
                if "API_KEY_INVALID" in message or "invalid api key" in message.lower():
                    st.error("The API key appears invalid. Check your Gemini API key.")
                elif "429" in message or "RESOURCE_EXHAUSTED" in message:
                    st.error("The API usage limit may have been reached. Wait a little and try again.")
                else:
                    st.error(f"Could not generate the quiz: {message}")
                st.caption("Check your internet connection and API key, then try again.")

quiz_data = st.session_state.get("quiz_data")
if quiz_data:
    st.divider()
    st.subheader(quiz_data.get("title", "Your practice quiz"))
    st.caption(
        f"Topic: {st.session_state.get('quiz_topic', '')} · "
        f"Difficulty: {st.session_state.get('quiz_level', '')}"
    )

    with st.form("answer_form"):
        selected_answers = {}
        for i, question in enumerate(quiz_data.get("questions", []), start=1):
            st.markdown(f"**{i}. {question.get('question', 'Question')}**")
            options = question.get("options", [])
            if len(options) != 4:
                st.warning("One question did not contain four options. You can still review the other questions.")
            selected_answers[str(i)] = st.radio(
                "Choose one answer:",
                options=options,
                index=None,
                key=f"answer_{i}_{st.session_state.get('quiz_topic', '')}",
                label_visibility="collapsed",
            )
            st.write("")
        checked = st.form_submit_button("Check my answers", use_container_width=True)

    if checked:
        correct = 0
        total = len(quiz_data.get("questions", []))
        for i, question in enumerate(quiz_data.get("questions", []), start=1):
            chosen = selected_answers.get(str(i))
            answer = question.get("answer", "")
            is_correct = chosen is not None and chosen.strip() == answer.strip()
            if is_correct:
                correct += 1
            with st.container(border=True):
                if is_correct:
                    st.markdown(f"**Question {i}: ✅ Correct**")
                elif chosen is None:
                    st.markdown(f"**Question {i}: ⚪ Not answered**")
                else:
                    st.markdown(f"**Question {i}: ❌ Not quite**")
                st.write(f"**Correct answer:** {answer}")
                explanation = question.get("explanation", "")
                if explanation:
                    st.write(f"**Explanation:** {explanation}")
        st.success(f"Your score: {correct} out of {total} ({round(correct / total * 100)}%)")

st.markdown("---")
st.markdown(
    '<p class="small-note">Made as a learning project. AI-generated questions can '
    'sometimes be wrong, so check important answers against your class notes or textbook.</p>',
    unsafe_allow_html=True,
)
