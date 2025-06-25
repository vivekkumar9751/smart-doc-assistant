from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from backend.document_utils import extract_text_from_pdf, extract_text_from_txt
from backend.qa_logic import generate_summary, answer_question  # ✅ both functions now

app = FastAPI()

# CORS settings (needed for Streamlit frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
doc_store = {"content": "", "summary": ""}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_bytes = await file.read()

    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif file.filename.endswith(".txt"):
        text = extract_text_from_txt(file_bytes)
    else:
        return {"error": "Unsupported file type. Please upload PDF or TXT."}

    # Save document content in memory
    doc_store["content"] = text

    # ✅ Generate Summary using GPT
    summary = generate_summary(text)
    doc_store["summary"] = summary

    return {
        "message": "File uploaded successfully.",
        "document_size": f"{len(text)} characters",
        "summary": summary,
        "preview": text[:500]
    }

# Helper endpoint to get current document
@app.get("/doc/")
def get_document():
    return {
        "document": doc_store["content"][:500],
        "summary": doc_store["summary"]
    }
from pydantic import BaseModel  # Add this at the top if missing

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask/")
def ask_question(data: QuestionRequest):
    if not doc_store["content"]:
        return {"error": "No document uploaded yet."}

    answer = answer_question(doc_store["content"], data.question)
    return {
        "question": data.question,
        "answer": answer
    }
