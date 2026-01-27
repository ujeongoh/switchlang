import streamlit as st
from google import genai
from google.genai import types
import os
import json
import pandas as pd
from dotenv import load_dotenv

# 1. Load Environment Variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Configure Streamlit Page
st.set_page_config(
    page_title="SwitchLang AI Tutor",
    page_icon="🔄",
    layout="wide"
)

# 3. Initialize Gemini Client (New SDK Style)
if not api_key:
    st.error("Error: GEMINI_API_KEY not found in .env file.")
    client = None
else:
    client = genai.Client(api_key=api_key)

# 4. Helper Function: Call Gemini API
def get_ai_feedback(user_text, input_lang, output_lang):
    """
    Sends the user's text to gemini.
    """
    if not client:
        return {"error": "API Key missing"}

    prompt = f"""
    You are a professional language tutor.
    The user is practicing converting sentences from {input_lang} to {output_lang}.
    
    Analyze the following text: "{user_text}"
    
    Your task:
    1. Identify the intent of the text.
    2. Provide a natural translation in {output_lang}.
    3. If the input was already in {output_lang}, correct the grammar and nuance.
    4. Provide a brief explanation.
    
    Output must be a valid JSON object with keys:
    - original_text
    - improved_text
    - explanation
    - score (1-5 integer)
    """

    try:
        response = client.models.generate_content(
            model='gemini-3-flash-preview', 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": str(e)}

# 5. UI Layout (Sidebar)
with st.sidebar:
    st.title("🔄 SwitchLang")
    st.caption("Powered by Google Gemini 3.0 Flash")
    
    st.header("Settings")
    input_lang = st.selectbox("Input Language", ["Korean", "English", "Japanese", "Spanish"], index=0)
    output_lang = st.selectbox("Target Language", ["English", "Korean", "Japanese", "Spanish"], index=1)
    
    st.divider()
    st.info(f"Mode: {input_lang} ➡ {output_lang}")

# 6. UI Layout (Main Area)
st.title("Active Recall Practice 📝")
st.write("Type a sentence, and AI will polish or translate it for you.")

# User Input
user_input = st.text_area("Enter your sentence:", height=100, placeholder="e.g., 오늘 회의가 3시로 미뤄졌어.")

if st.button("Switch & Check ✨", type="primary"):
    if not user_input:
        st.warning("Please enter a sentence first.")
    else:
        with st.spinner("AI is analyzing..."):
            result = get_ai_feedback(user_input, input_lang, output_lang)
            
            if "error" in result:
                st.error(f"AI Error: {result['error']}")
            else:
                st.success("Analysis Complete!")
                
                # Format data
                data = {
                    "Category": ["Original", "Improved / Translated", "Explanation", "Score"],
                    "Content": [
                        result.get("original_text"),
                        result.get("improved_text"),
                        result.get("explanation"),
                        f"{'⭐' * int(result.get('score', 0))}/5"
                    ]
                }
                
                df = pd.DataFrame(data)
                st.table(df)