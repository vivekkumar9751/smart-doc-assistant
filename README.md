# 📋 Smart Document Assistant

A powerful AI-powered document processing application that provides intelligent summarization, question-answering, and comprehension testing capabilities. Built with FastAPI backend and Streamlit frontend, powered by Groq's lightning-fast LLaMA models.

## ✨ Features

- **📄 Document Upload**: Support for PDF and TXT files up to 50MB
- **🤖 AI-Powered Summarization**: Automatic document summarization using Groq's LLaMA models
- **❓ Intelligent Q&A**: Ask questions about your documents and get accurate answers
- **🎯 Challenge Mode**: Generate multiple-choice questions to test document comprehension
- **⚡ Lightning Fast**: Powered by Groq's optimized inference engine for rapid responses
- **🔒 Secure**: Local processing with secure API key management
- **📱 User-Friendly Interface**: Clean, intuitive Streamlit frontend

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Groq API key ([Get one here](https://console.groq.com/keys))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-doc-assistant
   ```

2. **Install dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```
   Replace `your_groq_api_key_here` with your actual Groq API key.

4. **Run the application**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

5. **Access the application**
   Open your browser and go to: `http://localhost:8501`

## 🔧 Manual Setup

If you prefer to run services separately:

### Backend (FastAPI)
```bash
python3 -m uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

### Frontend (Streamlit)
```bash
python3 -m streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

## 📋 Usage

1. **Upload Document**: Choose a PDF or TXT file from your computer
2. **Auto-Summary**: Get an instant AI-generated summary of your document
3. **Ask Questions**: Type questions about the document content
4. **Challenge Mode**: Test your understanding with AI-generated multiple-choice questions
5. **Reset**: Upload a new document anytime to start fresh

## 🏗️ Architecture

```
Smart Document Assistant
├── backend/
│   ├── api.py           # FastAPI server and endpoints
│   ├── qa_logic.py      # Groq API integration and AI logic
│   └── document_utils.py # Document processing utilities
├── frontend/
│   └── app.py           # Streamlit user interface
├── .env                 # Environment variables (not in git)
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
└── README.md           # Project documentation
```

## 🔌 API Endpoints

### Health Check
```
GET /health
```
Returns the API health status.

### Document Upload
```
POST /upload/
```
Upload and process a document file.

### Generate Summary
```
POST /summarize
```
Generate an AI summary of the uploaded document.

### Ask Question
```
POST /ask
```
Ask a question about the document content.

### Challenge Questions
```
POST /challenge
```
Generate multiple-choice questions for comprehension testing.

## 🛠️ Technologies Used

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Groq**: Lightning-fast AI inference platform
- **PyMuPDF**: PDF text extraction
- **Python-multipart**: File upload handling
- **Uvicorn**: ASGI web server

### Frontend
- **Streamlit**: Rapid web app development framework
- **Python**: Core programming language

### AI Models
- **LLaMA 3 (8B)**: Via Groq's optimized inference engine

## 📊 Performance

- **Groq Integration**: Sub-second response times for most queries
- **File Processing**: Supports documents up to 50MB
- **Concurrent Users**: Handles multiple simultaneous requests
- **Memory Efficient**: Optimized text processing and chunking

## 🔐 Security Features

- **API Key Validation**: Secure Groq API key handling
- **File Size Limits**: Prevents oversized uploads
- **Input Sanitization**: Clean and validate all user inputs
- **Error Handling**: Comprehensive error management and logging

## 🚦 Environment Variables

Create a `.env` file with the following:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## 📝 Logging

The application provides comprehensive logging for:
- API requests and responses
- Document processing status
- Error tracking and debugging
- Performance monitoring

## 🔧 Development

### Project Structure
```
├── backend/           # API server code
├── frontend/          # Web interface code
├── requirements.txt   # Dependencies
├── .env              # Environment config
├── start.sh          # Startup script
└── README.md         # Documentation
```

### Running in Development Mode

1. **Start Backend**:
   ```bash
   python3 -m uvicorn backend.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend**:
   ```bash
   python3 -m streamlit run frontend/app.py --server.port 8501
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Requirements

See `requirements.txt` for a complete list of dependencies. Key packages:

- `fastapi>=0.115.13`
- `streamlit>=1.46.0`
- `groq>=0.29.0`
- `PyMuPDF>=1.26.1`
- `python-multipart>=0.0.20`
- `uvicorn>=0.34.3`

## 🐛 Troubleshooting

### Common Issues

1. **"Command not found" errors**:
   - Make sure you're using `python3` and `pip3`
   - Check if packages are installed: `pip3 list`

2. **Port already in use**:
   - Kill existing processes: `pkill -f uvicorn` or `pkill -f streamlit`
   - Use different ports in the startup commands

3. **API key issues**:
   - Ensure `.env` file exists and contains valid Groq API key
   - Check key format starts with `gsk_`

4. **File upload issues**:
   - Check file size (max 50MB)
   - Ensure file is PDF or TXT format

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Groq** for providing lightning-fast AI inference
- **Streamlit** for the amazing web app framework
- **FastAPI** for the modern, fast web framework
- **LLaMA** models for powerful language understanding

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the application logs for error messages
3. Open an issue on GitHub with detailed information

---

**Built with ❤️ using Groq's lightning-fast AI models**
