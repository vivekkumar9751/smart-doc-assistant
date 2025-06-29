import os
import time
import re
from typing import List
from dotenv import load_dotenv
from groq import Groq
import logging
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def validate_api_key(api_key: str) -> bool:
    """Validate Groq API key format"""
    if not api_key:
        return False
    
    if not api_key.startswith('gsk_'):
        return False
    
    api_key = api_key.strip().replace('\n', '').replace(' ', '')
    
    if len(api_key) < 20:
        return False
        
    return True

def get_validated_api_key():
    """Get and validate API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError(
            "❌ GROQ_API_KEY not found in environment variables. "
            "Please check your .env file and ensure it's properly configured."
        )
    
    api_key = api_key.strip().replace('\n', '').replace(' ', '')
    
    if not validate_api_key(api_key):
        raise ValueError(
            "❌ GROQ_API_KEY format is invalid. "
            "Please ensure your API key is correct and on a single line."
        )
    
    return api_key

try:
    api_key = get_validated_api_key()
    client = Groq(api_key=api_key)
    logger.info("✅ Groq API client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Groq client: {str(e)}")
    raise

def handle_groq_errors(func):
    """Decorator to handle Groq API errors consistently"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "exceeded" in error_msg:
                return (
                    "❌ API quota exceeded. Please check your Groq account at "
                    "https://console.groq.com/. You may need to add more credits or upgrade your plan."
                )
            elif "invalid" in error_msg and "api" in error_msg:
                return (
                    "❌ Invalid API key. Please check your Groq API key in the .env file. "
                    "Get a new key at https://console.groq.com/keys"
                )
            elif "rate" in error_msg and "limit" in error_msg:
                return (
                    "❌ Rate limit exceeded. Please wait a moment and try again. "
                    "Consider upgrading your Groq plan for higher rate limits."
                )
            elif "timeout" in error_msg:
                return "❌ Request timeout. Please try again with a shorter document or check your internet connection."
            else:
                logger.error(f"Unexpected API error: {str(e)}")
                return f"❌ API Error: {str(e)}"
    
    return wrapper

def safe_chat_completion_create(**kwargs):
    """Make API calls with retry logic and proper error handling"""
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
                
            response = client.chat.completions.create(**kwargs)
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            
            if "quota" in error_msg or "exceeded" in error_msg:
                raise Exception(
                    "API quota exceeded. Please check your Groq billing at https://console.groq.com/"
                )
            elif "invalid" in error_msg and ("key" in error_msg or "token" in error_msg):
                raise Exception(
                    "Invalid API key. Please check your GROQ_API_KEY in .env file"
                )
            elif "rate" in error_msg and "limit" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"⚠️ Rate limit hit (attempt {attempt + 1}/{max_retries}), retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please try again later or upgrade your Groq plan.")
            elif attempt < max_retries - 1:
                wait_time = base_delay * (2 ** attempt)
                logger.warning(f"⚠️ API error (attempt {attempt + 1}/{max_retries}): {str(e)}, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            else:
                raise e
    
    raise Exception("Failed after maximum retries")

@handle_groq_errors
def generate_summary(document_text):
    """Generate document summary with enhanced error handling"""
    try:
        logger.info("Generating document summary...")
        
        text_for_summary = document_text[:4000] if len(document_text) > 4000 else document_text
        
        prompt = (
            "Summarize the following document in no more than 150 words. "
            "Focus on key ideas, main points, and important details:\n\n"
            f"{text_for_summary}"
        )

        response = safe_chat_completion_create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
            timeout=30
        )

        summary = response.choices[0].message.content.strip()
        logger.info("✅ Summary generated successfully")
        return summary
        
    except Exception as e:
        logger.error(f"❌ Error generating summary: {str(e)}")
        raise e

@handle_groq_errors
def answer_question(document_text, user_question):
    """Answer user questions with enhanced error handling"""
    try:
        logger.info(f"Processing question: {user_question[:50]}...")
        
        context_text = document_text[:4000] if len(document_text) > 4000 else document_text
        
        prompt = (
            "You are a helpful assistant. Based only on the document below, "
            "answer the user's question accurately and concisely. "
            "If the answer is not in the document, say so clearly.\n\n"
            f"Document:\n{context_text}\n\n"
            f"Question: {user_question}\n\n"
            "Answer:"
        )

        response = safe_chat_completion_create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300,
            timeout=30
        )

        answer = response.choices[0].message.content.strip()
        logger.info("✅ Question answered successfully")
        return answer
        
    except Exception as e:
        logger.error(f"❌ Error answering question: {str(e)}")
        raise e

@handle_groq_errors
def generate_challenge_questions(document_text):
    """Generate challenge questions with enhanced error handling"""
    try:
        logger.info("Generating challenge questions...")
        
        text_for_challenge = document_text[:3000] if len(document_text) > 3000 else document_text
        
        prompt = (
            "Based on the following document, create exactly 3 multiple-choice questions "
            "to test comprehension. For each question, provide 4 options (A, B, C, D) "
            "and indicate the correct answer. Format your response as:\n\n"
            "Question 1: [question text]\n"
            "A) [option A]\n"
            "B) [option B]\n"
            "C) [option C]\n"
            "D) [option D]\n"
            "Correct Answer: [A/B/C/D]\n\n"
            "Continue this format for all 3 questions.\n\n"
            f"Document:\n{text_for_challenge}"
        )

        response = safe_chat_completion_create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
            timeout=45
        )

        questions_text = response.choices[0].message.content.strip()
        
        questions = parse_challenge_questions(questions_text)
        
        logger.info(f"✅ Generated {len(questions)} challenge questions successfully")
        return questions
        
    except Exception as e:
        logger.error(f"❌ Error generating challenge questions: {str(e)}")
        raise e

@handle_groq_errors
def evaluate_user_answers(document_text, qa_pairs: List[dict]):
    """Evaluate user answers with enhanced error handling"""
    try:
        logger.info("Evaluating user answers...")
        
        evaluation_items = []
        for i, qa in enumerate(qa_pairs, 1):
            evaluation_items.append(f"Question {i}: {qa['question']}")
            evaluation_items.append(f"User Answer: {qa['user_answer']}")
            evaluation_items.append(f"Correct Answer: {qa['correct_answer']}")
            evaluation_items.append("")
        
        evaluation_text = "\n".join(evaluation_items)
        
        prompt = (
            "Evaluate the user's answers to these questions based on the document. "
            "For each question, determine if the user's answer is correct and provide brief feedback. "
            "Format your response as:\n\n"
            "Question 1: ✅ Correct / ❌ Incorrect\n"
            "Feedback: [brief explanation]\n\n"
            "Then provide an overall score and summary.\n\n"
            f"Document excerpt:\n{document_text[:2000]}\n\n"
            f"Questions and Answers to evaluate:\n{evaluation_text}"
        )

        response = safe_chat_completion_create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
            timeout=40
        )

        evaluation = response.choices[0].message.content.strip()
        logger.info("✅ User answers evaluated successfully")
        return evaluation
        
    except Exception as e:
        logger.error(f"❌ Error evaluating answers: {str(e)}")
        raise e

def parse_challenge_questions(questions_text):
    """Parse generated questions into structured format"""
    questions = []
    lines = questions_text.split('\n')
    current_question = {}
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('Question '):
            if current_question:
                questions.append(current_question)
            current_question = {'question': line.split(':', 1)[1].strip()}
        elif line.startswith(('A)', 'B)', 'C)', 'D)')):
            option_key = line[0].lower()
            option_text = line[2:].strip()
            if 'options' not in current_question:
                current_question['options'] = {}
            current_question['options'][option_key] = option_text
        elif line.startswith('Correct Answer:'):
            current_question['correct_answer'] = line.split(':', 1)[1].strip().lower()
    
    if current_question:
        questions.append(current_question)
    
    return questions

def health_check():
    """Health check function for the API"""
    try:
        if client:
            return {"status": "healthy", "service": "groq", "message": "Groq API client is ready"}
        else:
            return {"status": "unhealthy", "message": "Groq client not initialized"}
    except Exception as e:
        return {"status": "unhealthy", "message": f"Health check failed: {str(e)}"}
