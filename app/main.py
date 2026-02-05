import streamlit as st
import pandas as pd
from services.ai_service import AIService
from services.db_service import init_db, save_result, get_history

# 1. Page Configuration
st.set_page_config(
    page_title="SwitchLang AI Tutor v3.5",
    page_icon="🧠",
    layout="wide"
)

# 2. Initialize Services
init_db()  # Ensure DB is created
ai_service = AIService()

# 3. Initialize Session State
if 'quiz_data' not in st.session_state:
    st.session_state['quiz_data'] = []
if 'mode' not in st.session_state:
    st.session_state['mode'] = "init" 

# --- UI Layout ---

st.title("🧠 SwitchLang: Active Recall Practice")

# Sidebar Navigation
with st.sidebar:
    st.header("📌 Menu")
    page = st.radio("Go to", ["Practice", "History"])
    st.divider()

    if page == "Practice":
        st.header("⚙️ Settings")
        input_lang = st.selectbox("Input Language (Source)", ["Korean", "English", "Japanese", "Spanish"], index=0)
        output_lang = st.selectbox("Output Language (Target)", ["Korean", "English", "Japanese", "Spanish"], index=1)
        
        st.divider()
        
        difficulty = st.select_slider(
            "Difficulty Level",
            options=["Beginner", "Intermediate", "Advanced"],
            value="Intermediate"
        )
        
        st.divider()
        mode = st.radio("Select Generation Mode", ["1. AI Generated Questions", "2. Custom Input Questions"])

# --- PAGE 1: PRACTICE ---
if page == "Practice":
    st.markdown(f"**Mode:** {mode} | **Level:** {difficulty}")

    # Mode 1: AI Generated
    if mode == "1. AI Generated Questions":
        num_questions = st.number_input("Number of expressions (n)", min_value=1, max_value=50, value=10)
        
        if st.button("Generate New Questions (Reset)"):
            with st.spinner(f"AI is extracting {difficulty} expressions..."):
                expressions = ai_service.generate_expressions(input_lang, num_questions, difficulty)
                st.session_state['quiz_data'] = [{"source": exp, "user_input": "", "feedback": None} for exp in expressions]
                st.rerun()

    # Mode 2: Custom Input
    elif mode == "2. Custom Input Questions":
        user_source_text = st.text_area(
            "Enter sentences to practice (one per line)", 
            height=150, 
            placeholder="Example:\nIt's raining cats and dogs.\nCould you loop me in on that email?"
        )
        
        if st.button("Start Practice"):
            lines = [line.strip() for line in user_source_text.split('\n') if line.strip()]
            if lines:
                st.session_state['quiz_data'] = [{"source": line, "user_input": "", "feedback": None} for line in lines]
                st.rerun()
            else:
                st.warning("Please enter at least one sentence.")

    st.divider()

    # Quiz Interface
    if st.session_state['quiz_data']:
        st.write(f"### 📝 Practice Table ({len(st.session_state['quiz_data'])} Questions)")
        
        col1, col2, col3 = st.columns([1, 1.5, 1.5])
        col1.markdown(f"**Source ({input_lang})**")
        col2.markdown(f"**Your Translation ({output_lang})**")
        col3.markdown("**AI Feedback**")
        
        for i, item in enumerate(st.session_state['quiz_data']):
            with st.container():
                c1, c2, c3 = st.columns([1, 1.5, 1.5])
                
                # 1. Source
                c1.info(item['source'])
                
                # 2. User Input
                user_val = c2.text_input(
                    label="translate", 
                    key=f"input_{i}", 
                    label_visibility="collapsed",
                    value=item['user_input'],
                    placeholder="Type translation here"
                )
                st.session_state['quiz_data'][i]['user_input'] = user_val
                
                # 3. Feedback & Save Logic
                if item['feedback']:
                    if "Yes" in item['feedback'] or "Correct" in item['feedback']:
                        c3.success(item['feedback'])
                    else:
                        c3.markdown(item['feedback']) # Use markdown to render bold text
                else:
                    if c3.button("Check", key=f"check_{i}"):
                        with st.spinner("Checking..."):
                            feedback = ai_service.get_evaluation(item['source'], user_val, input_lang, output_lang)
                            st.session_state['quiz_data'][i]['feedback'] = feedback
                            
                            # Save to Database automatically
                            save_result(input_lang, output_lang, item['source'], user_val, feedback)
                            st.rerun()
        
        st.divider()
        
        # Check All Button
        if st.button("Check All Answers"):
            progress_bar = st.progress(0)
            for i, item in enumerate(st.session_state['quiz_data']):
                if not item['feedback'] and item['user_input']: 
                    feedback = ai_service.get_evaluation(item['source'], item['user_input'], input_lang, output_lang)
                    st.session_state['quiz_data'][i]['feedback'] = feedback
                    # Save to DB
                    save_result(input_lang, output_lang, item['source'], item['user_input'], feedback)
                progress_bar.progress((i + 1) / len(st.session_state['quiz_data']))
            st.rerun()

    else:
        st.info("Please generate or enter questions above to start practicing!")

# --- PAGE 2: HISTORY ---
elif page == "History":
    st.header("📜 Study History")
    st.markdown("Review your past practice sessions and AI feedback.")
    
    df = get_history()
    
    if not df.empty:
        # Display as a dataframe with search capability
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Date", format="D MMM YYYY, h:mm a"),
                "source_text": "Source",
                "user_input": "Your Input",
                "feedback": "AI Feedback"
            }
        )
        
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download History as CSV",
            data=csv,
            file_name='switchlang_history.csv',
            mime='text/csv',
        )
    else:
        st.info("No history found. Go to the Practice page to start learning!")