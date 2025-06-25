import os
import openai
from dotenv import load_dotenv

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_summary(document_text):
    prompt = (
        "Summarize the following document in no more than 150 words. "
        "Focus on key ideas and structure:\n\n"
        f"{document_text[:3000]}"  # Avoid token overload
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
        max_tokens=200
    )

    return response.choices[0].message["content"].strip()

def answer_question(document_text, user_question):
    prompt = (
        "You are a helpful assistant. Based only on the document below, "
        "answer the user's question. At the end of your answer, briefly justify "
        "which section or paragraph supports your answer (e.g., 'This is supported by paragraph 2').\n\n"
        f"Document:\n{document_text[:3000]}\n\n"
        f"Question: {user_question}"
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=300
    )

    return response.choices[0].message["content"].strip()
