import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Document Assistant", layout="wide")
st.title("📄 Smart Assistant for Research Summarization")

# Session state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False

# ---- Upload File ----
st.header("📁 Upload a Document (PDF or TXT)")
uploaded_file = st.file_uploader("Choose a document", type=["pdf", "txt"])

if uploaded_file and not st.session_state.uploaded:
    with st.spinner("Uploading and processing..."):
        files = {"file": uploaded_file.getvalue()}
        response = requests.post(f"{API_URL}/upload/", files={"file": (uploaded_file.name, uploaded_file.getvalue())})

        if response.status_code == 200:
            try:
                data = response.json()
                st.session_state.summary = data["summary"]
                st.session_state.preview = data["preview"]
                st.session_state.uploaded = True
            except requests.exceptions.JSONDecodeError:
                st.error("Server returned an invalid JSON response during upload.")
        else:
            try:
                error_message = response.json().get("error", "Something went wrong")
            except requests.exceptions.JSONDecodeError:
                error_message = f"Server returned status {response.status_code}: {response.text}"
            st.error(error_message)

# ---- Show Summary and Preview ----
if st.session_state.uploaded:
    st.success("✅ Document uploaded successfully!")
    st.subheader("🔍 Auto Summary")
    st.write(st.session_state.summary)

    with st.expander("📖 Preview of Uploaded Text"):
        st.code(st.session_state.preview)

# ---- Ask Anything ----
if st.session_state.uploaded:
    st.header("🤖 Ask Anything")
    question = st.text_input("Enter your question")

    if st.button("Get Answer") and question:
        res = requests.post(f"{API_URL}/ask/", json={"question": question})
        if res.status_code == 200:
            try:
                st.write("💬 **Answer:**")
                st.success(res.json()["answer"])
            except requests.exceptions.JSONDecodeError:
                st.error("Invalid response from server.")
        else:
            try:
                error_message = res.json().get("error", "Something went wrong")
            except requests.exceptions.JSONDecodeError:
                error_message = f"Server returned status {res.status_code}: {res.text}"
            st.error(error_message)

# ---- Challenge Me Mode ----
if st.session_state.uploaded:
    st.header("🧠 Challenge Me")

    if st.button("Generate Challenge Questions"):
        qres = requests.get(f"{API_URL}/challenge/")
        if qres.status_code == 200:
            try:
                questions = qres.json()["questions"]
                st.session_state.challenge_qs = questions
                st.session_state.answers = [""] * len(questions)
            except requests.exceptions.JSONDecodeError:
                st.error("Failed to parse questions from server.")
        else:
            try:
                error_message = qres.json().get("error", "Something went wrong")
            except requests.exceptions.JSONDecodeError:
                error_message = f"Server returned status {qres.status_code}: {qres.text}"
            st.error(error_message)

    if "challenge_qs" in st.session_state:
        st.subheader("📝 Your Answers")
        for idx, q in enumerate(st.session_state.challenge_qs):
            st.session_state.answers[idx] = st.text_input(f"Q{idx+1}: {q}", key=f"q{idx}")

        if st.button("Evaluate Answers"):
            payload = {
                "responses": [
                    {"question": q, "answer": a}
                    for q, a in zip(st.session_state.challenge_qs, st.session_state.answers)
                ]
            }
            eval_res = requests.post(f"{API_URL}/evaluate/", json=payload)
            if eval_res.status_code == 200:
                try:
                    st.subheader("📊 Feedback")
                    for item in eval_res.json()["feedback"]:
                        st.markdown(f"**Q:** {item['question']}")
                        st.markdown(f"**Your Answer:** {item['user_answer']}")
                        st.markdown(f"**Evaluation:** {item['evaluation']}")
                        st.markdown("---")
                except requests.exceptions.JSONDecodeError:
                    st.error("Error parsing evaluation feedback from server.")
            else:
                try:
                    error_message = eval_res.json().get("error", "Something went wrong")
                except requests.exceptions.JSONDecodeError:
                    error_message = f"Server returned status {eval_res.status_code}: {eval_res.text}"
                st.error(error_message)
