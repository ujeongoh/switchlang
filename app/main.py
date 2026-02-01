import streamlit as st
from google import genai
import os

# 1. Page Configuration
st.set_page_config(
    page_title="SwitchLang AI Tutor v3.5",
    page_icon="🧠",
    layout="wide"
)

# 2. Gemini API Setup (Client-based for google-genai SDK)
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("🚨 GEMINI_API_KEY environment variable is missing.")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_NAME = 'gemini-3-flash-preview' 

# 3. Initialize Session State
if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []
if 'mode' not in st.session_state:
    st.session_state['mode'] = "init" 

# --- Helper Functions ---

def generate_expressions(src_lang, count, difficulty):
    """Request Gemini to list expressions based on difficulty."""
    
    # Dynamic prompt based on difficulty level
    difficulty_instruction = ""
    if difficulty == "Beginner":
        difficulty_instruction = "Use simple, essential daily phrases for survival and basic greetings."
    elif difficulty == "Intermediate":
        difficulty_instruction = "Use natural conversational sentences expressing feelings, opinions, or situations. Avoid 1-word greetings."
    elif difficulty == "Advanced":
        difficulty_instruction = "Use sophisticated vocabulary, idioms, slangs, or professional business expressions. The sentences should sound like a native speaker."

    prompt = f"""
    List {count} useful expressions used in {src_lang}.
    
    Target Level: {difficulty}
    Style Guide: {difficulty_instruction}
    
    Constraint: Do not include translations. Just the list of source text.
    Output format: A simple list separated by newlines.
    """
    
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        expressions = [line.strip() for line in response.text.split('\n') if line.strip()]
        return expressions
    except Exception as e:
        st.error(f"Error generating expressions: {e}")
        return []

def get_evaluation(src_text, user_text, src_lang, tgt_lang):
    """Evaluate user's translation."""
    if not user_text:
        return "No input provided."
    
    prompt = f"""
    Task: Evaluate a language translation practice.
    
    Source Language: {src_lang}
    Target Language: {tgt_lang}
    
    Source Text: "{src_text}"
    User's Translation: "{user_text}"
    
    1. Is the user's translation grammatically and contextually correct? (Yes/No)
    2. If No or if it can be improved, provide the most natural native translation.
    3. Keep the feedback concise (max 2 sentences).
    """
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error during evaluation: {str(e)}"

# --- UI Layout ---

st.title("🧠 SwitchLang: Active Recall Practice")
st.markdown("Interactive Language Writing Training with AI")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Settings")
    input_lang = st.selectbox("Input Language (Source)", ["Korean", "English", "Japanese", "Spanish"], index=0)
    output_lang = st.selectbox("Output Language (Target)", ["Korean", "English", "Japanese", "Spanish"], index=1)
    
    st.divider()
    
    # Difficulty Selector (New Feature)
    difficulty = st.select_slider(
        "Difficulty Level",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate"
    )
    
    st.divider()
    st.markdown("**Feature Selection**")
    mode = st.radio("Select Mode", ["1. AI Generated Questions", "2. Custom Input Questions"])

# --- Main Logic ---

# Mode 1: AI Generated
if mode == "1. AI Generated Questions":
    st.subheader(f"🤖 Translate {input_lang} expressions into {output_lang}")
    st.caption(f"Current Level: {difficulty}")
    
    num_questions = st.number_input("Number of expressions (n)", min_value=1, max_value=50, value=10)
    
    if st.button("Generate New Questions (Reset)"):
        with st.spinner(f"AI is extracting {difficulty} expressions..."):
            # Pass difficulty to function
            expressions = generate_expressions(input_lang, num_questions, difficulty)
            
            # Reset session data
            st.session_state['quiz_data'] = [{"source": exp, "user_input": "", "feedback": None} for exp in expressions]
            st.rerun()

# Mode 2: Custom Input
elif mode == "2. Custom Input Questions":
    st.subheader(f"✍️ Practice Custom Sentences ({input_lang})")
    
    user_source_text = st.text_area(
        "Enter sentences to practice (one per line)", 
        height=150, 
        placeholder="Example:\nIt's raining cats and dogs.\nCould you loop me in on that email?\nI'm on the fence about it."
    )
    
    if st.button("Start Practice"):
        lines = [line.strip() for line in user_source_text.split('\n') if line.strip()]
        if lines:
            st.session_state['quiz_data'] = [{"source": line, "user_input": "", "feedback": None} for line in lines]
            st.rerun()
        else:
            st.warning("Please enter at least one sentence.")

# --- Quiz Interface (Common) ---

st.divider()

if st.session_state['quiz_data']:
    st.write(f"### 📝 Practice Table ({len(st.session_state['quiz_data'])} Questions)")
    
    # Table Headers
    col1, col2, col3 = st.columns([1, 1.5, 1.5])
    col1.markdown(f"**Source ({input_lang})**")
    col2.markdown(f"**Your Translation ({output_lang})**")
    col3.markdown("**AI Feedback**")
    
    # Render List
    for i, item in enumerate(st.session_state['quiz_data']):
        with st.container():
            c1, c2, c3 = st.columns([1, 1.5, 1.5])
            
            # 1. Source Text
            c1.info(item['source'])
            
            # 2. User Input
            user_val = c2.text_input(
                label="translate", 
                key=f"input_{i}", 
                label_visibility="collapsed",
                value=item['user_input'],
                placeholder="Type your translation here"
            )
            # Bind input to session state
            st.session_state['quiz_data'][i]['user_input'] = user_val
            
            # 3. Feedback Area
            if item['feedback']:
                if "Yes" in item['feedback'] or "Correct" in item['feedback']:
                    c3.success(item['feedback'])
                else:
                    c3.warning(item['feedback'])
            else:
                if c3.button("Check", key=f"check_{i}"):
                    with st.spinner("Checking..."):
                        feedback = get_evaluation(item['source'], user_val, input_lang, output_lang)
                        st.session_state['quiz_data'][i]['feedback'] = feedback
                        st.rerun()
    
    st.divider()
    
    # Check All Button
    if st.button("Check All Answers"):
        progress_bar = st.progress(0)
        for i, item in enumerate(st.session_state['quiz_data']):
            if not item['feedback'] and item['user_input']: 
                feedback = get_evaluation(item['source'], item['user_input'], input_lang, output_lang)
                st.session_state['quiz_data'][i]['feedback'] = feedback
            progress_bar.progress((i + 1) / len(st.session_state['quiz_data']))
        st.rerun()

else:
    st.info("Please generate or enter questions above to start practicing!")