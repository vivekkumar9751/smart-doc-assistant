from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import asyncio
import logging
import os

from backend.document_utils import extract_text_from_pdf, extract_text_from_txt
from backend.qa_logic import (
    generate_summary,
    answer_question,
    generate_challenge_questions,
    evaluate_user_answers,
    health_check as openai_health_check
)

import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Document Assistant API", version="1.0.0")

# Enhanced CORS config for frontend access
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

# Enhanced upload endpoint with better error handling and timeouts
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Starting upload for file: {file.filename}")
        
        # Validate file size (limit to 50MB)
        if file.size and file.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Maximum size is 50MB.")
        
        # Read file with timeout
        try:
            file_bytes = await asyncio.wait_for(file.read(), timeout=30.0)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="File upload timeout. Please try a smaller file.")
        
        filename = file.filename.lower()
        logger.info(f"Processing file: {filename}, size: {len(file_bytes)} bytes")

        # Extract text based on file type
        if filename.endswith(".pdf"):
            text = await asyncio.get_event_loop().run_in_executor(
                None, extract_text_from_pdf, file_bytes
            )
        elif filename.endswith(".txt"):
            text = await asyncio.get_event_loop().run_in_executor(
                None, extract_text_from_txt, file_bytes
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or TXT.")

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="The file appears to be empty or unreadable.")

        logger.info(f"Text extracted successfully: {len(text)} characters")
        
        # Store document content
        doc_store["content"] = text
        
        # Generate summary with timeout
        try:
            summary = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, generate_summary, text),
                timeout=60.0
            )
            doc_store["summary"] = summary
        except asyncio.TimeoutError:
            summary = "Summary generation timed out. Please try again with a smaller document."
            doc_store["summary"] = summary
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
                summary = "❌ OpenAI quota exceeded. Please check your billing at https://platform.openai.com/usage"
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
                summary = "❌ Invalid API key. Please check your .env configuration."
            else:
                summary = f"❌ Error generating summary: {error_msg}"
            doc_store["summary"] = summary

        logger.info("Upload and processing completed successfully")
        
        return JSONResponse(content={
            "message": "File uploaded and processed successfully.",
            "document_size": f"{len(text)} characters",
            "summary": summary,
            "preview": text[:500] + ("..." if len(text) > 500 else "")
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /upload/: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during file processing: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check for the API"""
    return {"status": "healthy", "message": "API is running"}

# OpenAI health check endpoint
@app.get("/health/openai")
async def openai_health():
    """Check OpenAI API connectivity and quota status"""
    try:
        health_result = await asyncio.get_event_loop().run_in_executor(
            None, openai_health_check
        )
        return health_result
    except Exception as e:
        return {
            "status": "unhealthy", 
            "message": f"OpenAI API check failed: {str(e)}"
        }

# Environment info endpoint (for debugging)
@app.get("/health/env")
async def environment_info():
    """Get environment information for debugging"""
    return {
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "python_version": os.sys.version,
        "api_key_configured": bool(os.getenv("OPENAI_API_KEY")),
        "api_key_format_valid": bool(os.getenv("OPENAI_API_KEY", "").startswith("sk-"))
    }

# Get document summary
@app.get("/doc/")
def get_document():
    return {
        "document": doc_store["content"][:500] + ("..." if len(doc_store["content"]) > 500 else ""),
        "summary": doc_store["summary"]
    }

# Ask a question with improved error handling
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
async def ask_question(data: QuestionRequest):
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        # Process question with timeout
        answer = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, answer_question, doc_store["content"], data.question
            ),
            timeout=45.0
        )
        
        return {
            "question": data.question,
            "answer": answer
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Question processing timed out. Please try a simpler question.")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in /ask/: {error_msg}")
        
        # Handle specific OpenAI errors
        if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            raise HTTPException(status_code=429, detail="OpenAI quota exceeded. Please check your billing.")
        elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        else:
            raise HTTPException(status_code=500, detail="Error answering the question.")

# Generate challenge questions with timeout
@app.get("/challenge/")
async def challenge_questions():
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        questions = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, generate_challenge_questions, doc_store["content"]
            ),
            timeout=45.0
        )
        doc_store["challenge_questions"] = questions

        return {
            "questions": questions
        }
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Challenge question generation timed out.")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in /challenge/: {error_msg}")
        
        # Handle specific OpenAI errors
        if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            raise HTTPException(status_code=429, detail="OpenAI quota exceeded. Please check your billing.")
        elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        else:
            raise HTTPException(status_code=500, detail="Error generating challenge questions.")

# Evaluate user answers with timeout
class AnswerItem(BaseModel):
    question: str
    answer: str

class AnswerRequest(BaseModel):
    responses: List[AnswerItem]

@app.post("/evaluate/")
async def evaluate_answers(data: AnswerRequest):
    try:
        if not doc_store["content"]:
            raise HTTPException(status_code=400, detail="No document uploaded yet.")

        feedback = await asyncio.wait_for(
            asyncio.get_event_loop().run_in_executor(
                None, evaluate_user_answers, doc_store["content"], data.responses
            ),
            timeout=60.0
        )
        return {"feedback": feedback}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Answer evaluation timed out.")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in /evaluate/: {error_msg}")
        
        # Handle specific OpenAI errors
        if "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            raise HTTPException(status_code=429, detail="OpenAI quota exceeded. Please check your billing.")
        elif "invalid" in error_msg.lower() and "key" in error_msg.lower():
            raise HTTPException(status_code=401, detail="Invalid OpenAI API key.")
        else:
            raise HTTPException(status_code=500, detail="Error evaluating answers.")