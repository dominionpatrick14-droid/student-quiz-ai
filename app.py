
import json
import os
import streamlit as st
from google import genai
from google.genai import types


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Student Quiz AI",
    page_icon="📚",
    layout="centered",
)

st.title("📚 Student Quiz AI")
st.write(
    "Choose a topic, generate practice questions, "
    "and test what you know."
)


# ---------------- API KEY ----------------

def get_api_key():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GEMINI_API_KEY", "")


# ---------------- QUIZ GENERATION ----------------

def generate_quiz(api_key, subject, topic, difficulty, count):
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=45000),
    )

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
                            "items": {"type": "STRING"},
                        },
                        "answer": {"type": "STRING"},
                        "explanation": {"type": "STRING"},
                    },
                    "required": [
                        "question",
                        "options",
                        "answer",
                        "explanation",
                    ],
                },
            },
        },
        "required": ["title", "questions"],
    }

    prompt = f"""
Create exactly {count} multiple-choice practice questions.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Rules:
- Give exactly 4 options for each question.
- Make the options different and relevant.
- The answer must exactly match one option.
- Keep explanations to one short sentence.
- Avoid repeating questions.
- Return only the requested structured quiz.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.3,
            max_output_tokens=1200,
        ),
    )

    if not response.text:
        raise ValueError(
            "The AI returned an empty response. Please try again."
        )

    quiz = json.loads(response.text)
    questions = quiz.get("questions", [])

    if len(questions) != count:
        raise ValueError(
            f"The AI returned {len(questions)} questions "
            f"instead of {count}. Please try again."
        )

    for number, question in enumerate(questions, start=1):
        options = question.get("options", [])
        answer = question.get("answer", "")

        if len(options) != 4:
            raise ValueError(
                f"Question {number} does not have exactly 4 options."
            )

        if answer not in options:
            raise ValueError(
                f"Question {number} has an invalid answer. "
                "Please generate the quiz again."
            )

    return quiz


# ---------------- QUIZ SETTINGS ----------------

subject = st.selectbox(
    "Choose a subject",
    [
        "Mathematics",
        "English",
        "Biology",
        "Chemistry",
        "Physics",
        "Computer Science",
        "General Knowledge",
        "Business Studies",
        "Other",
    ],
)

topic = st.text_input(
    "Enter your topic",
    placeholder="Example: Photosynthesis",
)

difficulty = st.selectbox(
    "Choose difficulty",
    ["Easy", "Medium", "Hard"],
)

count = st.slider(
    "Number of questions",
    min_value=3,
    max_value=10,
    value=3,
)

generate_button = st.button(
    "Generate Quiz",
    type="primary",
    use_container_width=True,
)


# ---------------- GENERATE AND SAVE QUIZ ----------------

if generate_button:
    api_key = get_api_key()

    if not api_key:
        st.error(
            "API key not found. Add GEMINI_API_KEY "
            "in your Streamlit app's Secrets settings."
        )
        st.stop()

    if not topic.strip():
        st.warning("Please enter a topic first.")
        st.stop()

    st.session_state.pop("quiz", None)
    st.session_state.pop("submitted_answers", None)
    st.session_state.pop("score", None)

    try:
        with st.spinner(
            "Creating your questions. This should not take minutes..."
        ):
            quiz = generate_quiz(
                api_key=api_key,
                subject=subject,
                topic=topic.strip(),
                difficulty=difficulty,
                count=count,
            )

        st.session_state["quiz"] = quiz
        st.session_state["submitted_answers"] = {}

    except Exception as error:
        message = str(error)
        lower_message = message.lower()

        if "timeout" in lower_message or "timed out" in lower_message:
            st.error(
                "The AI took too long to respond. "
                "Try again shortly."
            )
        elif "429" in message or "resource_exhausted" in lower_message:
            st.error(
                "The AI service limit has been reached. "
                "Wait a little before trying again."
            )
        elif (
            "503" in message
            or "unavailable" in lower_message
            or "overloaded" in lower_message
        ):
            st.error(
                "The AI service is busy right now. "
                "Please try again later."
            )
        elif (
            "401" in message
            or "403" in message
            or "api key" in lower_message
            or "permission denied" in lower_message
        ):
            st.error(
                "The API key may be invalid or lack permission. "
                "Check your Streamlit Secrets settings."
            )
        else:
            st.error(f"Quiz generation failed: {message}")


# ---------------- DISPLAY QUIZ ----------------

if "quiz" in st.session_state:
    quiz = st.session_state["quiz"]

    st.divider()
    st.subheader(quiz.get("title", "Your Practice Quiz"))

    with st.form("quiz_answer_form"):
        selected_answers = {}

        for index, question in enumerate(
            quiz["questions"]
        ):
            st.markdown(
                f"**Question {index + 1}: "
                f"{question['question']}**"
            )

            selected_answers[index] = st.radio(
                "Choose your answer:",
                question["options"],
                index=None,
                key=f"answer_{index}",
                label_visibility="collapsed",
            )

        submitted = st.form_submit_button(
            "Check My Answers",
            use_container_width=True,
        )

    if submitted:
        score = 0

        for index, question in enumerate(quiz["questions"]):
            if selected_answers[index] == question["answer"]:
                score += 1

        st.session_state["submitted_answers"] = selected_answers
        st.session_state["score"] = score

    if "score" in st.session_state:
        score = st.session_state["score"]
        total = len(quiz["questions"])

        st.divider()
        st.subheader(f"Your Score: {score}/{total}")
        st.progress(score / total)

        for index, question in enumerate(quiz["questions"]):
            chosen = st.session_state["submitted_answers"][index]
            correct = question["answer"]

            st.markdown(f"**Question {index + 1}**")

            if chosen == correct:
                st.success(f"Correct! {correct}")
            else:
                st.error(
                    f"Your answer: {chosen or 'Not answered'}"
                )
                st.info(f"Correct answer: {correct}")

            st.write(f"Explanation: {question['explanation']}")

        if st.button("Generate Another Quiz"):
            st.session_state.pop("quiz", None)
            st.session_state.pop("submitted_answers", None)
            st.session_state.pop("score", None)
            st.rerun()
