import streamlit as st
import google.generativeai as genai
import json
import time

# ---------------- CONFIG ----------------
st.set_page_config(page_title="RBI Assistant Simulator", layout="wide")
st.title("🏦 RBI Assistant Smart Prep System")

# ---------------- API SETUP ----------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    st.error("Add GEMINI_API_KEY in Streamlit secrets")
    st.stop()

# ---------------- SESSION STATE ----------------
if "questions" not in st.session_state:
    st.session_state.questions = []

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ---------------- TOPIC ----------------
topic = st.selectbox(
    "Select Topic",
    ["Banking Awareness", "Economy", "Insurance", "Current Affairs"]
)

news_input = st.text_area("Paste News Here", height=150)

# ---------------- GENERATE QUESTIONS ----------------
if st.button("Generate MCQs"):

    if news_input:
        with st.spinner("Generating exam-level questions..."):

            prompt = f"""
            Act as RBI Assistant examiner.

            Create 5 MCQs from this news:

            {news_input}

            Return ONLY JSON format:
            [
              {{
                "question": "",
                "options": ["A", "B", "C", "D", "E"],
                "answer": "A",
                "explanation": ""
              }}
            ]
            """

            try:
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "max_output_tokens": 1000
                    }
                )

                text = response.text.strip()
                text = text.replace("```json", "").replace("```", "")

                questions = json.loads(text)

                st.session_state.questions = questions
                st.session_state.quiz_started = True
                st.session_state.user_answers = {}
                st.session_state.start_time = None
                st.session_state.submitted = False

                st.success("✅ Questions generated!")

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Paste news first!")

# ---------------- START TEST ----------------
if st.session_state.quiz_started and st.session_state.start_time is None:

    if st.button("🚀 Start Test"):
        st.session_state.start_time = time.time()

# ---------------- TIMER ----------------
if st.session_state.start_time and not st.session_state.submitted:

    total_time = 60 * 60  # 60 minutes
    elapsed = time.time() - st.session_state.start_time
    remaining = int(total_time - elapsed)

    minutes = remaining // 60
    seconds = remaining % 60

    st.warning(f"⏳ Time Left: {minutes}m {seconds}s")

    if remaining <= 0:
        st.session_state.submitted = True
        st.error("⛔ Time Up! Auto-submitting...")

# ---------------- QUESTIONS ----------------
if st.session_state.start_time and not st.session_state.submitted:

    st.subheader("📝 Attempt Questions")

    for i, q in enumerate(st.session_state.questions):

        st.markdown(f"### Q{i+1}. {q['question']}")

        selected = st.radio(
            f"Answer Q{i+1}",
            q["options"],
            key=f"q{i}"
        )

        st.session_state.user_answers[i] = selected

# ---------------- SUBMIT ----------------
if st.session_state.start_time and not st.session_state.submitted:

    if st.button("Submit Test"):
        st.session_state.submitted = True

# ---------------- RESULT ----------------
if st.session_state.submitted:

    score = 0
    correct = 0
    wrong = 0

    st.subheader("📊 Result Analysis")

    for i, q in enumerate(st.session_state.questions):

        user = st.session_state.user_answers.get(i, None)
        ans = q["answer"]

        if user == ans:
            score += 1
            correct += 1
        else:
            if user:
                score -= 0.25
                wrong += 1

    total = len(st.session_state.questions)
    accuracy = (correct / total) * 100 if total > 0 else 0

    cutoff = total * 0.6  # 60% cutoff

    st.markdown(f"""
    ## 🎯 Final Score: {score:.2f}

    ✅ Correct: {correct}  
    ❌ Wrong: {wrong}  
    📌 Accuracy: {accuracy:.2f}%  
    """)

    if score >= cutoff:
        st.success("✅ Status: CLEARED (Above Cutoff)")
    else:
        st.error("❌ Status: NOT CLEARED")

    # ---------------- SOLUTIONS ----------------
    st.subheader("🧠 Detailed Solutions")

    for i, q in enumerate(st.session_state.questions):

        st.markdown(f"### Q{i+1}")

        st.write(f"Correct Answer: {q['answer']}")
        st.info(q["explanation"])

# ---------------- SAVE ----------------
if st.session_state.questions:

    if st.button("💾 Save Questions"):

        with open("questions.json", "w") as f:
            json.dump(st.session_state.questions, f, indent=4)

        st.success("Saved successfully!")
