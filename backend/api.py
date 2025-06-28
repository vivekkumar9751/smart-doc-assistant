from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

from backend.document_utils import extract_text_from_pdf, extract_text_from_txt
from backend.qa_logic import (
    generate_summary,
    answer_question,
    generate_challenge_questions,
    evaluate_user_answers
)

import traceback

app = FastAPI()

# CORS config for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
doc_store = {
    "content": "",
    "summary": "",
    "challenge_questions": []
}

# Upload and summarize
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith(".txt"):
            text = extract_text_from_txt(file_bytes)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or TXT.")

        if not text.strip():
            raise HTTPException(status_code=400, detail="The file is empty or unreadable.")

        doc_store["content"] = text
        summary = generate_summary(text)
        doc_store["summary"] = summary

        return JSONResponse(content={
            "message": "File uploaded successfully.",
            "document_size": f"{len(text)} characters",
            "summary": summary,
            "preview": text[:500]
        })

    except Exception as e:
        print("❌ Error in /upload/:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during file upload: {str(e)}")

# Get document summary
@app.get("/doc/")
def get_document():
    return {
        "document": doc_store["content"][:500],
        "summary": doc_store["summary"]
    }

# Ask a question
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
def ask_question(data: QuestionRequest):
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        answer = answer_question(doc_store["content"], data.question)
        return {
            "question": data.question,
            "answer": answer
        }
    except Exception as e:
        print("❌ Error in /ask/:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error answering the question.")

# Generate challenge questions
@app.get("/challenge/")
def challenge_questions():
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        questions = generate_challenge_questions(doc_store["content"])
        doc_store["challenge_questions"] = questions

        return {
            "questions": questions
        }
    except Exception as e:
        print("❌ Error in /challenge/:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error generating challenge questions.")

# Evaluate user answers
class AnswerItem(BaseModel):
    question: str
    answer: str

class AnswerRequest(BaseModel):
    responses: List[AnswerItem]

@app.post("/evaluate/")
def evaluate_answers(data: AnswerRequest):
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        feedback = evaluate_user_answers(doc_store["content"], data.responses)
        return {"feedback": feedback}
    except Exception as e:
        print("❌ Error in /evaluate/:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error evaluating answers.")