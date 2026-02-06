import streamlit as st
import pandas as pd
import logging
import sys

from services.ai_service import AIService
from services.db_service import init_db, save_result, get_history

# --- logger settings ---
root_logger = logging.getLogger()
if root_logger.handlers:
    root_logger.handlers = []

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # send logs in std output (for Docker)
    ]
)
logger = logging.getLogger(__name__)

# 1. Page Configuration
st.set_page_config(
    page_title="SwitchLang AI Tutor v3.7", 
    page_icon="🧠", 
    layout="wide"
)

logger.info("🚀 SwitchLang App Started")

# 2. Initialize Services
try:
    init_db()
    ai_service = AIService()
    logger.info("✅ Services initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize services: {e}", exc_info=True)
    st.error("System Error: Check server logs.")
    st.stop()

# 3. Initialize Session State
if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []
if 'mode' not in st.session_state:
    st.session_state['mode'] = "init" 

# --- UI Layout ---

st.title("🧠 SwitchLang: Active Recall Practice")

# Sidebar
with st.sidebar:
    st.header("📌 Menu")
    page = st.radio("Go to", ["Practice", "History"])
    st.divider()

    if page == "Practice":
        st.header("⚙️ Settings")
        input_lang = st.selectbox("Input Language", ["Korean", "English", "Japanese", "Spanish"], index=0)
        output_lang = st.selectbox("Output Language", ["Korean", "English", "Japanese", "Spanish"], index=1)
        st.divider()
        difficulty = st.select_slider("Difficulty Level", options=["Beginner", "Intermediate", "Advanced"], value="Intermediate")
        st.divider()
        mode = st.radio("Select Generation Mode", ["1. AI Generated Questions", "2. Custom Input Questions"])

# --- PAGE 1: PRACTICE ---
if page == "Practice":
    st.markdown(f"**Mode:** {mode} | **Level:** {difficulty}")

    # Mode 1: AI Generated
    if mode == "1. AI Generated Questions":
        num_questions = st.number_input("Number of expressions", min_value=1, max_value=50, value=10)
        if st.button("Generate New Questions (Reset)"):
            with st.spinner(f"AI is extracting {difficulty} expressions..."):
                expressions = ai_service.generate_expressions(input_lang, num_questions, difficulty)
                st.session_state['quiz_data'] = [{"source": exp, "user_input": "", "feedback": None} for exp in expressions]
                st.rerun()

    # Mode 2: Custom Input
    elif mode == "2. Custom Input Questions":
        user_source_text = st.text_area("Enter sentences to practice", height=150)
        if st.button("Start Practice"):
            lines = [line.strip() for line in user_source_text.split('\n') if line.strip()]
            if lines:
                logger.info(f"User input custom questions: {len(lines)} lines")
                st.session_state['quiz_data'] = [{"source": line, "user_input": "", "feedback": None} for line in lines]
                st.rerun()

    st.divider()

    # Quiz Interface (5 columns)
    if st.session_state['quiz_data']:
        st.write(f"### 📝 Practice Table ({len(st.session_state['quiz_data'])} Questions)")
        
        # ratio: Source(1) | Input(1.5) | Grammar(1.5) | Native(1.5) | Explain(2)
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 1.5, 1.5, 2])
        col1.markdown(f"**Source ({input_lang})**")
        col2.markdown(f"**Your Input ({output_lang})**")
        col3.markdown("**Grammar Fix**")
        col4.markdown("**✨ Native Best**")
        col5.markdown("**Explanation**")
        
        for i, item in enumerate(st.session_state['quiz_data']):
            with st.container():
                c1, c2, c3, c4, c5 = st.columns([1, 1.5, 1.5, 1.5, 2])
                
                # 1. Source
                c1.info(item['source'])
                
                # 2. User Input
                user_val = c2.text_input(
                    label="translate", 
                    key=f"input_{i}", 
                    label_visibility="collapsed",
                    value=item['user_input']
                )
                st.session_state['quiz_data'][i]['user_input'] = user_val
                
                # Feedback Handling
                feedback = item['feedback']
                
                if feedback:
                    is_correct = feedback.get('is_correct', False)
                    corrected_text = feedback.get('corrected', '')
                    better_text = feedback.get('better_expression', '')
                    explanation_text = feedback.get('explanation', '')

                    # 3. Grammar Fix Column
                    if is_correct:
                        c3.success("Grammar OK")
                    else:
                        c3.error(f"{corrected_text}")

                    # 4. Native Best Column
                    c4.info(f"**{better_text}**") 

                    # 5. Explanation
                    c5.caption(explanation_text)

                else:
                    if c5.button("Check", key=f"check_{i}"):
                        with st.spinner("Checking..."):
                            logger.info(f"Checking answer for: {item['source']}")
                            result_dict = ai_service.get_evaluation(item['source'], user_val, input_lang, output_lang)
                            st.session_state['quiz_data'][i]['feedback'] = result_dict
                            
                            # save in DB
                            save_result(input_lang, output_lang, item['source'], user_val, str(result_dict))
                            st.rerun()
        
        st.divider()
        
        # Check All Button
        if st.button("Check All Answers"):
            
            # 1. get ready for checking the data (call API once)
            with st.spinner("Checking all answers at once..."):
                
                batch_results = ai_service.evaluate_batch(
                    st.session_state['quiz_data'], 
                    input_lang, 
                    output_lang
                )
                
                # 2. Map results with Session State and Save to DB
                processed_count = 0
                for i, feedback in batch_results.items():
                    if i < len(st.session_state['quiz_data']):
                        item = st.session_state['quiz_data'][i]
                        item['feedback'] = feedback
                        
                        save_result(input_lang, output_lang, item['source'], item['user_input'], str(feedback))
                        processed_count += 1
                
                if processed_count > 0:
                    st.success(f"✅ {processed_count} items checked successfully!")
                    st.rerun()
                else:
                    st.warning("No new answers to check.")

    else:
        st.info("Start via settings above!")

# --- PAGE 2: HISTORY ---
elif page == "History":
    st.header("📜 Study History")
    df = get_history()
    if not df.empty:
        # map with db column names
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, h:mm a"),
                "source_text": "Source",
                "user_input": "Your Input",
                "feedback": "AI Feedback (JSON)"
            }
        )
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download History as CSV",
            data=csv,
            file_name='switchlang_history.csv',
            mime='text/csv',
        )
    else:
        st.info("No history found. Go to the Practice page to start learning!")