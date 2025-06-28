# ✅ Updated qa_logic.py for OpenAI API with modern client

import os
import time
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not loaded properly. Check your .env setup.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)
logger.info("✅ OPENAI_API_KEY loaded successfully.")

# Enhanced retry wrapper for rate limiting and errors
def safe_chat_completion_create(**kwargs):
    for attempt in range(3):
        try:
            return client.chat.completions.create(**kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle quota exceeded specifically
            if "insufficient_quota" in error_msg or "exceeded your current quota" in error_msg:
                logger.error("🚫 OpenAI API quota exceeded!")
                raise Exception(
                    "🚫 OpenAI API quota exceeded. Please:\n"
                    "1. Check your OpenAI billing: https://platform.openai.com/account/billing\n"
                    "2. Add payment method or upgrade your plan\n"
                    "3. Or try again later if on free tier\n"
                    "The app will use fallback responses until this is resolved."
                )
            
            # Handle rate limits (temporary)
            elif "rate_limit" in error_msg or "rate limit" in error_msg:
                wait_time = 2 ** attempt  # Exponential backoff
                logger.warning(f"⚠️ Rate limit hit (attempt {attempt + 1}/3), retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            
            # Handle other API errors
            elif attempt == 2:  # Last attempt
                logger.error(f"❌ Failed after 3 retries: {str(e)}")
                raise e
            else:
                logger.warning(f"⚠️ API error (attempt {attempt + 1}/3): {str(e)}")
                time.sleep(1)
    
    raise Exception("❌ Failed after 3 retries due to API errors.")

def generate_summary(document_text):
    try:
        logger.info("Generating document summary...")
        
        # Limit text length for summary generation
        text_for_summary = document_text[:4000] if len(document_text) > 4000 else document_text
        
        prompt = (
            "Summarize the following document in no more than 150 words. "
            "Focus on key ideas, main points, and important details:\n\n"
            f"{text_for_summary}"
        )

        response = safe_chat_completion_create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
            timeout=30
        )

        summary = response.choices[0].message.content.strip()
        logger.info("Summary generated successfully")
        return summary
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating summary: {error_msg}")
        
        # Provide fallback summary when quota exceeded
        if "quota exceeded" in error_msg or "insufficient_quota" in error_msg:
            return (
                "⚠️ AI Summary unavailable (OpenAI quota exceeded)\n\n"
                "📄 FALLBACK SUMMARY:\n"
                f"Document contains {len(document_text)} characters. "
                f"Here's the beginning:\n\n{document_text[:300]}...\n\n"
                "💡 To get AI-powered summaries, please check your OpenAI billing settings."
            )
        
        return f"Error generating summary: {error_msg}"

def answer_question(document_text, user_question):
    try:
        logger.info(f"Processing question: {user_question[:50]}...")
        
        # Limit context for better performance
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
            timeout=30
        )

        answer = response.choices[0].message.content.strip()
        logger.info("Question answered successfully")
        return answer
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error answering question: {error_msg}")
        
        # Provide fallback response when quota exceeded
        if "quota exceeded" in error_msg or "insufficient_quota" in error_msg:
            return (
                "⚠️ AI Q&A unavailable (OpenAI quota exceeded)\n\n"
                "📝 FALLBACK RESPONSE:\n"
                f"I cannot provide an AI-powered answer to: '{user_question}'\n\n"
                "You can manually search the document for relevant information. "
                "To restore AI functionality, please check your OpenAI billing settings."
            )
        
        return f"Error processing your question: {error_msg}"

def generate_challenge_questions(document_text):
    try:
        logger.info("Generating challenge questions...")
        
        # Limit context for better performance
        context_text = document_text[:4000] if len(document_text) > 4000 else document_text
        
        prompt = (
            "Based on the document below, generate exactly 3 comprehension questions "
            "that test understanding of key concepts. Make them thought-provoking but answerable. "
            "Return only the questions, numbered 1-3, one per line:\n\n"
            f"Document:\n{context_text}"
        )

        response = safe_chat_completion_create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=400,
            timeout=30
        )

        questions_raw = response.choices[0].message.content.strip()
        
        # Parse questions more reliably
        questions = []
        for line in questions_raw.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('Q')):
                # Remove numbering and clean up
                clean_question = line.split('.', 1)[-1].strip()
                if clean_question:
                    questions.append(clean_question)
        
        # Ensure we have exactly 3 questions
        questions = questions[:3]
        if len(questions) < 3:
            questions.extend([
                "What are the main points discussed in this document?",
                "What conclusions can you draw from the information presented?",
                "How would you summarize the key findings or arguments?"
            ])
            questions = questions[:3]
            
        logger.info(f"Generated {len(questions)} challenge questions")
        return questions
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating challenge questions: {error_msg}")
        
        # Provide fallback questions when quota exceeded
        if "quota exceeded" in error_msg or "insufficient_quota" in error_msg:
            return [
                "⚠️ What are the main topics covered in this document? (AI generation unavailable - quota exceeded)",
                "⚠️ What are the key conclusions or findings mentioned? (Please check OpenAI billing)",
                "⚠️ What questions does this document raise for further research? (Fallback question)"
            ]
        
        return [
            "What are the main topics covered in this document?",
            "What are the key conclusions or findings?",
            "What questions does this document raise for further research?"
        ]

def evaluate_user_answers(document_text, qa_pairs: List[dict]):
    try:
        logger.info(f"Evaluating {len(qa_pairs)} user answers...")
        
        feedback = []
        context_text = document_text[:4000] if len(document_text) > 4000 else document_text

        for pair in qa_pairs:
            question = pair["question"]
            user_answer = pair["answer"]
            
            if not user_answer.strip():
                feedback.append({
                    "question": question,
                    "user_answer": "No answer provided",
                    "evaluation": "Please provide an answer to receive feedback."
                })
                continue

            prompt = (
                f"Document:\n{context_text}\n\n"
                f"Question: {question}\n"
                f"Student's Answer: {user_answer}\n\n"
                "Evaluate the student's answer based on the document. "
                "Provide constructive feedback on accuracy, completeness, and understanding. "
                "Be encouraging but honest about areas for improvement."
            )

            try:
                response = safe_chat_completion_create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=300,
                    timeout=30
                )

                evaluation = response.choices[0].message.content.strip()
                
            except Exception as e:
                error_msg = str(e)
                
                # Provide fallback evaluation when quota exceeded
                if "quota exceeded" in error_msg or "insufficient_quota" in error_msg:
                    evaluation = (
                        "⚠️ AI evaluation unavailable (OpenAI quota exceeded)\n\n"
                        f"Your answer: '{user_answer}'\n\n"
                        "Manual review suggested: Compare your answer with the document content. "
                        "For AI-powered feedback, please resolve the OpenAI billing issue."
                    )
                else:
                    evaluation = f"Error evaluating this answer: {error_msg}"

            feedback.append({
                "question": question,
                "user_answer": user_answer,
                "evaluation": evaluation
            })

        logger.info("Answer evaluation completed")
        return feedback
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error evaluating answers: {error_msg}")
        
        # Provide fallback when quota exceeded
        if "quota exceeded" in error_msg or "insufficient_quota" in error_msg:
            return [{
                "question": "OpenAI Quota Exceeded",
                "user_answer": "Service Unavailable",
                "evaluation": (
                    "⚠️ AI evaluation is currently unavailable due to OpenAI quota limits.\n\n"
                    "💡 To resolve this:\n"
                    "1. Visit: https://platform.openai.com/account/billing\n"
                    "2. Add payment method or upgrade your plan\n"
                    "3. Check your usage limits\n\n"
                    "The app will work normally once this is resolved."
                )
            }]
        
        return [{
            "question": "Error",
            "user_answer": "Error",
            "evaluation": f"Error during evaluation: {error_msg}"
        }]
