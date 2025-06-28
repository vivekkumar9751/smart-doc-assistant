import streamlit as st
import requests
import time

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Document Assistant", layout="wide")
st.title("📄 Smart Assistant for Research Summarization")

# Session state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

# Function to check backend health
def check_backend_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Check if backend is running
if not check_backend_health():
    st.error("🚨 Backend server is not running. Please start the backend server first.")
    st.info("Run this command in terminal: `python3 -m uvicorn backend.api:app --host 127.0.0.1 --port 8000`")
    st.stop()

# ---- Upload File ----
st.header("📁 Upload a Document (PDF or TXT)")
uploaded_file = st.file_uploader("Choose a document", type=["pdf", "txt"])

if uploaded_file and not st.session_state.uploaded:
    # Show file info
    file_size_mb = len(uploaded_file.getvalue()) / (1024 * 1024)
    st.info(f"📄 File: {uploaded_file.name} ({file_size_mb:.2f} MB)")
    
    # Check file size
    if file_size_mb > 50:
        st.error("❌ File too large! Please upload a file smaller than 50MB.")
    else:
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("Processing your document..."):
            try:
                status_text.text("📤 Uploading file...")
                progress_bar.progress(20)
                
                # Upload with longer timeout for large files
                timeout_seconds = max(60, int(file_size_mb * 10))  # Dynamic timeout based on file size
                
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = requests.post(
                    f"{API_URL}/upload/", 
                    files=files, 
                    timeout=timeout_seconds
                )
                
                progress_bar.progress(60)
                status_text.text("🔍 Extracting text...")
                
                if response.status_code == 200:
                    progress_bar.progress(80)
                    status_text.text("📝 Generating summary...")
                    
                    try:
                        data = response.json()
                        st.session_state.summary = data["summary"]
                        st.session_state.preview = data["preview"]
                        st.session_state.uploaded = True
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Processing complete!")
                        time.sleep(1)  # Show completion briefly
                        
                    except (requests.exceptions.JSONDecodeError, KeyError) as e:
                        st.error("❌ Server returned invalid data. Please try again.")
                        
                elif response.status_code == 413:
                    st.error("❌ File too large. Please upload a smaller file (max 50MB).")
                elif response.status_code == 408:
                    st.error("⏰ Upload timed out. Please try a smaller file or check your connection.")
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        st.error(f"❌ {error_data.get('detail', 'Invalid file format')}")
                    except:
                        st.error("❌ Invalid file format. Please upload PDF or TXT files only.")
                else:
                    try:
                        error_message = response.json().get("detail", "Something went wrong")
                    except requests.exceptions.JSONDecodeError:
                        error_message = f"Server error (Status {response.status_code})"
                    st.error(f"❌ {error_message}")
                    
            except requests.exceptions.Timeout:
                st.error("⏰ Upload timed out. Your file might be too large or the connection is slow. Please try again with a smaller file.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Cannot connect to the backend server. Please make sure it's running.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")
            finally:
                # Clean up progress indicators
                progress_bar.empty()
                status_text.empty()

# ---- Show Summary and Preview ----
if st.session_state.uploaded:
    st.success("✅ Document uploaded successfully!")
    
    # Summary Section
    st.subheader("🔍 Auto Summary")
    if "Summary generation timed out" in st.session_state.summary:
        st.warning("⚠️ Summary generation timed out. You can still ask questions about the document.")
    else:
        st.write(st.session_state.summary)

    # Preview Section
    with st.expander("📖 Preview of Uploaded Text"):
        st.code(st.session_state.preview, language="text")

# ---- Ask Anything ----
if st.session_state.uploaded:
    st.header("🤖 Ask Anything")
    question = st.text_input("Enter your question about the document")

    if st.button("Get Answer") and question:
        with st.spinner("🤔 Thinking..."):
            try:
                res = requests.post(
                    f"{API_URL}/ask/", 
                    json={"question": question},
                    timeout=60
                )
                if res.status_code == 200:
                    try:
                        st.write("💬 **Answer:**")
                        st.success(res.json()["answer"])
                    except requests.exceptions.JSONDecodeError:
                        st.error("❌ Invalid response from server.")
                elif res.status_code == 408:
                    st.error("⏰ Question processing timed out. Please try a simpler question.")
                else:
                    try:
                        error_message = res.json().get("detail", "Something went wrong")
                    except requests.exceptions.JSONDecodeError:
                        error_message = f"Server error (Status {res.status_code})"
                    st.error(f"❌ {error_message}")
            except requests.exceptions.Timeout:
                st.error("⏰ Question processing timed out. Please try a simpler question.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Cannot connect to the backend server.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ---- Challenge Me Mode ----
if st.session_state.uploaded:
    st.header("🧠 Challenge Me")

    if st.button("Generate Challenge Questions"):
        with st.spinner("🎯 Generating challenge questions..."):
            try:
                qres = requests.get(f"{API_URL}/challenge/", timeout=60)
                if qres.status_code == 200:
                    try:
                        questions = qres.json()["questions"]
                        st.session_state.challenge_qs = questions
                        st.session_state.answers = [""] * len(questions)
                    except requests.exceptions.JSONDecodeError:
                        st.error("❌ Failed to parse questions from server.")
                elif qres.status_code == 408:
                    st.error("⏰ Question generation timed out. Please try again.")
                else:
                    try:
                        error_message = qres.json().get("detail", "Something went wrong")
                    except requests.exceptions.JSONDecodeError:
                        error_message = f"Server error (Status {qres.status_code})"
                    st.error(f"❌ {error_message}")
            except requests.exceptions.Timeout:
                st.error("⏰ Question generation timed out. Please try again.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Cannot connect to the backend server.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

    if "challenge_qs" in st.session_state:
        st.subheader("📝 Your Answers")
        for idx, q in enumerate(st.session_state.challenge_qs):
            st.session_state.answers[idx] = st.text_input(f"Q{idx+1}: {q}", key=f"q{idx}")

        if st.button("Evaluate Answers"):
            with st.spinner("📊 Evaluating your answers..."):
                try:
                    payload = {
                        "responses": [
                            {"question": q, "answer": a}
                            for q, a in zip(st.session_state.challenge_qs, st.session_state.answers)
                        ]
                    }
                    eval_res = requests.post(
                        f"{API_URL}/evaluate/", 
                        json=payload,
                        timeout=90
                    )
                    if eval_res.status_code == 200:
                        try:
                            st.subheader("📊 Feedback")
                            for item in eval_res.json()["feedback"]:
                                st.markdown(f"**Q:** {item['question']}")
                                st.markdown(f"**Your Answer:** {item['user_answer']}")
                                st.markdown(f"**Evaluation:** {item['evaluation']}")
                                st.markdown("---")
                        except requests.exceptions.JSONDecodeError:
                            st.error("❌ Error parsing evaluation feedback from server.")
                    elif eval_res.status_code == 408:
                        st.error("⏰ Answer evaluation timed out. Please try again.")
                    else:
                        try:
                            error_message = eval_res.json().get("detail", "Something went wrong")
                        except requests.exceptions.JSONDecodeError:
                            error_message = f"Server error (Status {eval_res.status_code})"
                        st.error(f"❌ {error_message}")
                except requests.exceptions.Timeout:
                    st.error("⏰ Answer evaluation timed out. Please try again.")
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Cannot connect to the backend server.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ---- Reset Button ----
if st.session_state.uploaded:
    st.markdown("---")
    if st.button("🔄 Upload New Document"):
        st.session_state.uploaded = False
        st.session_state.summary = ""
        st.session_state.preview = ""
        if "challenge_qs" in st.session_state:
            del st.session_state.challenge_qs
        if "answers" in st.session_state:
            del st.session_state.answers
        st.rerun()
