# ✅ Updated qa_logic.py for Groq (Paste and replace fully)

import os
import time
from typing import List
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"

if not openai.api_key:
    raise ValueError("❌ GROQ_API_KEY not loaded properly. Check your .env setup.")
print("✅ GROQ_API_KEY loaded successfully.")

# Simple retry wrapper for rate limiting
def safe_chat_completion_create(**kwargs):
    for attempt in range(3):
        try:
            return openai.ChatCompletion.create(**kwargs)
        except openai.error.RateLimitError:
            print("⚠️ Rate limit hit, retrying in 2 seconds...")
            time.sleep(2)
    raise Exception("❌ Failed after 3 retries due to rate limiting.")

def generate_summary(document_text):
    prompt = (
        "Summarize the following document in no more than 150 words. "
        "Focus on key ideas and structure:\n\n"
        f"{document_text[:3000]}"
    )

    response = safe_chat_completion_create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200
    )

    return response.choices[0].message.content.strip()

def answer_question(document_text, user_question):
    prompt = (
        "You are a helpful assistant. Based only on the document below, "
        "answer the user's question and justify your answer with a supporting paragraph number or section. "
        "Do not hallucinate information.\n\n"
        f"Document:\n{document_text[:3000]}\n\n"
        f"Question: {user_question}"
    )

    response = safe_chat_completion_create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()

def generate_challenge_questions(document_text):
    prompt = (
        "Based on the document below, generate 3 logic-based or comprehension-focused questions that require reasoning. "
        "Do not include answers, only the questions, separated by new lines:\n\n"
        f"Document:\n{document_text[:3000]}"
    )

    response = safe_chat_completion_create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=400
    )

    questions_raw = response.choices[0].message.content.strip()
    questions = [q.strip() for q in questions_raw.split('\n') if q.strip()]
    return questions[:3]  # Ensure only 3 questions returned

def evaluate_user_answers(document_text, qa_pairs: List[dict]):
    feedback = []

    for pair in qa_pairs:
        question = pair["question"]
        user_answer = pair["answer"]

        prompt = (
            f"Document:\n{document_text[:3000]}\n\n"
            f"Question: {question}\n"
            f"User's Answer: {user_answer}\n\n"
            "Evaluate if the user's answer is correct, partially correct, or incorrect. "
            "Explain the reasoning clearly and cite the supporting paragraph if possible."
        )

        response = safe_chat_completion_create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )

        feedback.append({
            "question": question,
            "user_answer": user_answer,
            "evaluation": response.choices[0].message.content.strip()
        })

    return feedback
