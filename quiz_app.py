import streamlit as st
import datetime

# -------------------------
# ✅ Try importing Google Gemini SDK
# -------------------------
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("⚠ Module 'google-generativeai' not found. Make sure it is listed in requirements.txt")
    st.stop()

# -------------------------
# 🔑 Configure Gemini API Key
# -------------------------
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠ GOOGLE_API_KEY not found in Streamlit Secrets!")
    st.stop()

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# -------------------------
# 🎨 Styling
# -------------------------
st.markdown("""
<style>
.main-title { font-size:42px !important; color:#2C3E50 !important; font-weight:900 !important; text-align:center !important; }
.sub-title { font-size:22px !important; color:#222222 !important; font-weight:bold !important; margin-bottom:15px !important; }
div[data-testid="stTextInput"] label, div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label { color:#000000 !important; font-size:20px !important; font-weight:bold !important; }
input, textarea, select { font-size:18px !important; color:#000000 !important; background-color:#ffffff !important; }
::placeholder { color:#444444 !important; font-size:18px !important; }
button[kind="primary"] { font-size:18px !important; font-weight:bold !important; border-radius:10px !important; padding:10px 20px !important; background-color:#4CAF50 !important; color:white !important; }
button[kind="primary"]:hover { background-color:#45a049 !important; color:white !important; }
.stApp { background: linear-gradient(135deg, #74ebd5 0%, #ACB6E5 100%); }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 🌈 Quiz Generation Function
# -------------------------
def generate_quiz(topic, num_questions, q_type):
    prompt = f"""
    Generate {num_questions} quiz questions on the topic "{topic}".
    Question Type: {q_type}.
    
    Rules:
    - If MCQ: Provide 4 options (A-D) and the correct answer.
    - If Short Answer: Keep answers 1-2 sentences.
    - If Long Answer: Require detailed explanation (3-5 sentences).
    - If Mixed: Include a combination of MCQ, Short, and Long Answer.
    Format clearly with numbering.
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")  # Update if needed
    response = model.generate_content(prompt)
    
    # Safely extract text
    try:
        return response.candidates[0].content.parts[0].text
    except Exception:
        return "⚠ Error: Could not parse quiz response."

# -------------------------
# 🔑 Simple Login
# -------------------------
if "user" not in st.session_state:
    st.markdown('<div class="main-title">🔑 Login Page</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enter your name:</div>', unsafe_allow_html=True)

    username = st.text_input("", placeholder="Type your name here...")
    if st.button("Login"):
        if username.strip():
            st.session_state["user"] = username.strip()
            st.session_state["history"] = []
            st.rerun()
        else:
            st.error("⚠ Please enter a valid name.")

# -------------------------
# 👤 Main App after login
# -------------------------
else:
    st.sidebar.success(f"Welcome {st.session_state['user']} 🎉")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.markdown('<div class="main-title">🎓 AI Quiz Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Generate quizzes on any topic using Google Gemini AI</div>', unsafe_allow_html=True)

    topic = st.text_input("Enter a topic (e.g., Photosynthesis, Python Basics):")
    num_q = st.slider("Number of Questions", 3, 10, 5)
    q_type = st.selectbox("Question Type", ["MCQ", "Short Answer", "Long Answer", "Mixed"])

    if st.button("Generate Quiz"):
        if not topic.strip():
            st.error("⚠ Please enter a topic.")
        else:
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(topic, num_q, q_type)
                st.subheader("📘 Generated Quiz")
                st.text_area("Quiz", quiz, height=400)

                st.session_state["history"].append({
                    "user": st.session_state["user"],
                    "topic": topic,
                    "questions": num_q,
                    "type": q_type,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

    st.sidebar.subheader("📜 Your Activity History")
    if st.session_state["history"]:
        for entry in st.session_state["history"]:
            st.sidebar.write(
                f"{entry['topic']} ({entry['questions']} {entry['type']} Qs) on {entry['timestamp']}"
            )
    else:
        st.sidebar.write("No activity yet.")
