import os
import json
import logging
from google import genai
import streamlit as st

# Logger Setup
logger = logging.getLogger(__name__)

# Model Setup
MODEL_NAME = 'gemini-2.5-flash-lite'

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.critical("🚨 GEMINI_API_KEY is missing!")
            st.error("🚨 GEMINI_API_KEY environment variable is missing.")
            st.stop()
        self.client = genai.Client(api_key=self.api_key)

    def generate_expressions(self, src_lang, count, difficulty):
        """Generate expressions list based on difficulty."""
        logger.info(f"Generating {count} expressions for {src_lang} ({difficulty})")
        
        difficulty_instruction = ""
        
        if difficulty == "Beginner":
            difficulty_instruction = (
                "Use simple, short, and essential survival phrases. "
                "Focus on greetings, numbers, ordering food, and basic directions."
            )
        elif difficulty == "Intermediate":
            difficulty_instruction = (
                "Use **casual, natural sentences used by university students** talking to friends. "
                "Focus on: Campus life, exams, assignments, part-time jobs, dating, or hanging out after school. "
                "Tone: Friendly, casual (not too formal), and lively."
            )
        elif difficulty == "Advanced":
            difficulty_instruction = (
                "Strictly generate **sophisticated, modern, and professional** sentences used by educated native speakers in business or formal settings. "
                "Focus on: Negotiations, reporting, subtle emotional nuances, or persuasive arguments. "
                "**CONSTRAINT: ABSOLUTELY NO PROVERBS (e.g., 'Time flies'), NO OLD FOLK SAYINGS.** "
            )

        prompt = f"""
        Act as a language tutor. List {count} useful expressions in {src_lang}.
        
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
            
            logger.info(f"✅ Successfully generated {len(expressions)} expressions")
            return expressions
        except Exception as e:
            logger.error(f"❌ Error generating expressions: {e}", exc_info=True)
            st.error(f"Error generating expressions: {e}")
            return []

    def get_evaluation(self, src_text, user_text, src_lang, tgt_lang):
        """
        Evaluate user's translation and return structured JSON.
        """
        if not user_text:
            return {
                "is_correct": False, 
                "corrected": "", 
                "better_expression": "", 
                "explanation": "No input provided."
            }
        
        prompt = f"""
        Task: Evaluate a language translation practice.
        
        Source Language: {src_lang}
        Target Language: {tgt_lang}
        Source Text: "{src_text}"
        User's Translation: "{user_text}"
        
        Constraint: return ONLY a JSON object. Do not add markdown code blocks.
        
        JSON Schema:
        {{
            "is_correct": boolean, 
            "corrected": "string", // Grammar fix only. If correct, keep same as user input.
            "better_expression": "string", // The most natural, native-like (Native Best) way to say this in the context of the source text.
            "explanation": "string" // Explain the nuance difference or grammar error concisely.
        }}
        """
        
        try:
            logger.info(f"Requesting evaluation for: {src_text[:20]}...")
            
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)
            
            logger.info("✅ Evaluation successful")
            return result

        except json.JSONDecodeError:
            logger.error(f"❌ JSON Parsing Error. Raw output: {response.text}", exc_info=True)
            return {
                "is_correct": False,
                "corrected": "Error",
                "better_expression": "Error",
                "explanation": f"Parsing Error: {response.text}"
            }
        except Exception as e:
            logger.error(f"❌ Gemini API Error: {e}", exc_info=True)
            return {
                "is_correct": False,
                "corrected": "Error",
                "better_expression": "Error",
                "explanation": str(e)
            }
            
    def evaluate_batch(self, quiz_list, src_lang, tgt_lang):
        """
        Evaluate MULTIPLE items in a single API call.
        quiz_list: List of dicts [{'source': '...', 'user_input': '...'}, ...]
        """
        valid_items = [
            {"id": i, "source": q['source'], "user_input": q['user_input']} 
            for i, q in enumerate(quiz_list) 
            if q['user_input'].strip() and not q['feedback'] # 이미 피드백 받은 건 제외
        ]

        if not valid_items:
            return {}

        prompt = f"""
        Task: Evaluate a list of translation practices.
        
        Source Language: {src_lang}
        Target Language: {tgt_lang}
        
        Input Data (JSON List):
        {json.dumps(valid_items, ensure_ascii=False, indent=2)}
        
        Constraint: 
        1. Return ONLY a JSON object.
        2. The output must be a Dictionary where keys are the "id" from input, and values are the evaluation objects.
        3. Do not add markdown code blocks.
        
        Output JSON Schema:
        {{
            "0": {{
                "is_correct": boolean,
                "corrected": "string",
                "better_expression": "string",
                "explanation": "string"
            }},
            "1": {{ ... }}
        }}
        """

        try:
            logger.info(f"Batch evaluating {len(valid_items)} items...")
            
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )
            
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            result_dict = json.loads(clean_text) # {"0": {...}, "2": {...}} 형태
            
            final_result = {int(k): v for k, v in result_dict.items()}
            
            logger.info("✅ Batch evaluation successful")
            return final_result

        except Exception as e:
            logger.error(f"❌ Batch Evaluation Error: {e}", exc_info=True)
            return {}