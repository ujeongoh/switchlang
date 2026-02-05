import os
from google import genai
import streamlit as st

# Constants
MODEL_NAME = 'gemini-3-flash-preview' 

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            st.error("🚨 GEMINI_API_KEY environment variable is missing.")
            st.stop()
        self.client = genai.Client(api_key=self.api_key)

    def generate_expressions(self, src_lang, count, difficulty):
        """Request Gemini to list expressions based on difficulty."""
        
        difficulty_instruction = ""
        if difficulty == "Beginner":
            difficulty_instruction = "Use simple, essential daily phrases for survival and basic greetings."
        elif difficulty == "Intermediate":
            difficulty_instruction = "Use natural conversational sentences expressing feelings, opinions, or situations."
        elif difficulty == "Advanced":
            difficulty_instruction = "Use sophisticated vocabulary, idioms, slangs, or professional business expressions."

        prompt = f"""
        List {count} useful expressions used in {src_lang}.
        
        Target Level: {difficulty}
        Style Guide: {difficulty_instruction}
        
        Constraint: Do not include translations. Just the list of source text.
        Output format: A simple list separated by newlines.
        """
        
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            expressions = [line.strip() for line in response.text.split('\n') if line.strip()]
            return expressions
        except Exception as e:
            st.error(f"Error generating expressions: {e}")
            return []

    def get_evaluation(self, src_text, user_text, src_lang, tgt_lang):
        """Evaluate user's translation with formatting instructions."""
        if not user_text:
            return "No input provided."
        
        prompt = f"""
        Task: Evaluate a language translation practice.
        
        Source Language: {src_lang}
        Target Language: {tgt_lang}
        
        Source Text: "{src_text}"
        User's Translation: "{user_text}"
        
        Instructions:
        1. Is the translation grammatically and contextually correct?
        2. If it contains errors or is unnatural, provide the **Corrected Sentence** wrapped in bold markdown (e.g., **Corrected Sentence**).
        3. Provide a brief explanation.
        4. Keep the output concise (max 3 sentences).
        """
        try:
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error during evaluation: {str(e)}"