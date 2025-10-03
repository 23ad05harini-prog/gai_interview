import streamlit as st
import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# -------------------------
# Inject CSS for full-page gradient, no white space, cards, buttons, and inputs
# -------------------------
st.markdown(
    """
    <style>
    /* Hide Streamlit default header, footer, and menu */
    header, footer, #MainMenu {
        visibility: hidden;
        height: 0;
        padding: 0;
        margin: 0;
    }

    /* Remove top padding of the main container */
    .block-container {
        padding-top: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Full-page gradient background */
    .stApp {
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 50%, #fad0c4 100%);
        min-height: 100vh;
        color: #333333;
        font-family: 'Helvetica', sans-serif;
        margin: 0;
    }

    /* Card style for main content */
    .main-container {
        background-color: rgba(255, 255, 255, 0.9);
        padding: 30px;
        margin: 20px auto;
        border-radius: 20px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.15);
        max-width: 900px;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #a1c4fd 0%, #c2e9fb 100%);
        border-radius: 15px;
        padding: 20px;
        color: #000;
    }

    /* Button styling */
    div.stButton > button {
        background: linear-gradient(90deg, #ff758c 0%, #ff7eb3 100%);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 25px;
        font-weight: bold;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        background: linear-gradient(90deg, #ff7eb3 0%, #ff758c 100%);
    }

    /* Textarea styling */
    textarea {
        border-radius: 12px;
        padding: 10px;
        background-color: rgba(255,255,255,0.8);
    }

    /* Input fields & sliders */
    input, select, .stSlider > div {
        border-radius: 12px;
        padding: 8px;
        background-color: rgba(255,255,255,0.85);
        border: 1px solid #ccc;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# PDF Export Utility
# -------------------------
def generate_pdf(quiz_text, topic, username):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica", 12)
    width, height = A4

    c.setFont("Helvetica", 16)
    c.drawString(50, height - 50, f"Quiz on {topic}")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Generated for: {username}")
    c.line(50, height - 80, width - 50, height - 80)

    text_object = c.beginText(50, height - 110)
    text_object.setFont("Helvetica", 11)

    for line in quiz_text.splitlines():
        if text_object.getY() < 50:
            c.drawText(text_object)
            c.showPage()
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 11)
        text_object.textLine(line)

    c.drawText(text_object)
    c.save()
    buffer.seek(0)
    return buffer

# -------------------------
# Google Gemini SDK
# -------------------------
try:
    import google.generativeai as genai
except ModuleNotFoundError:
    st.error("⚠ Module 'google-generativeai' not found.")
    st.stop()

if "GOOGLE_API_KEY" not in st.secrets:
    st.error("⚠ GOOGLE_API_KEY not found in Streamlit Secrets!")
    st.stop()
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# -------------------------
# Quiz generation function
# -------------------------
def generate_quiz(topic: str, num_questions: int, q_type: str, bloom_level: str) -> str:
    prompt = f"""
    Generate {num_questions} quiz questions on the topic "{topic}".
    Question Type: {q_type}.
    Bloom's Taxonomy Level: {bloom_level}.
    Rules:
    - If MCQ: Provide 4 options (A-D) and the correct answer.
    - If Short Answer: Keep answers 1-2 sentences.
    - If Long Answer: Require detailed explanation (3-5 sentences).
    - If Mixed: Include a combination of MCQ, Short, and Long Answer.
    Format clearly with numbering.
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    try:
        return response.candidates[0].content.parts[0].text
    except Exception:
        return "⚠ Error: Could not parse quiz response."

# -------------------------
# Simple login
# -------------------------
if "user" not in st.session_state:
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown("## 🔑 Login Page")
    username = st.text_input("Enter your name:", placeholder="Type your name here...")
    if st.button("Login"):
        if username.strip():
            st.session_state["user"] = username.strip()
            st.session_state["history"] = []
            st.rerun()
        else:
            st.error("⚠ Please enter a valid name.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# Main app after login
# -------------------------
else:
    st.sidebar.success(f"Welcome {st.session_state['user']} 🎉")
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.title("🎓 AI Quiz Generator")
    st.subheader("Generate quizzes on any topic using Google Gemini AI")

    topic = st.text_input("Enter a topic (e.g., Photosynthesis, Python Basics):")
    num_q = st.slider("Number of Questions", 3, 10, 5)
    q_type = st.selectbox("Question Type", ["MCQ", "Short Answer", "Long Answer", "Mixed"])
    bloom = st.selectbox("Bloom’s Taxonomy Level", ["Knowledge", "Comprehension", "Application", "Analysis", "Synthesis", "Evaluation"])

    if st.button("Generate Quiz"):
        if not topic.strip():
            st.error("⚠ Please enter a topic.")
        else:
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(topic, num_q, q_type, bloom)
                st.subheader("📘 Generated Quiz")
                st.text_area("Quiz", quiz, height=400)

                # Save history
                st.session_state["history"].append({
                    "user": st.session_state["user"],
                    "topic": topic,
                    "questions": num_q,
                    "type": q_type,
                    "bloom": bloom,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                # Download PDF
                pdf_buffer = generate_pdf(quiz, topic, st.session_state["user"])
                st.download_button(
                    label="📥 Download Quiz as PDF",
                    data=pdf_buffer,
                    file_name=f"{topic}_quiz.pdf",
                    mime="application/pdf"
                )
    st.markdown('</div>', unsafe_allow_html=True)

    st.sidebar.subheader("📜 Your Activity History")
    if st.session_state["history"]:
        for entry in st.session_state["history"]:
            st.sidebar.write(
                f"{entry['topic']} ({entry['questions']} {entry['type']} Qs, {entry['bloom']}) on {entry['timestamp']}"
            )
    else:
        st.sidebar.write("No activity yet.")
