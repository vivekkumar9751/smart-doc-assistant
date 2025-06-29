#!/usr/bin/env python3
"""
Smart Document Assistant - Diagnostic Tool
This script helps identify and fix common deployment issues.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def print_status(message, status="INFO"):
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
    symbol = symbols.get(status, "ℹ️")
    print(f"{symbol} {message}")

def check_env_file():
    """Check .env file configuration"""
    print_status("Checking .env file configuration...")
    
    if not os.path.exists(".env"):
        print_status("No .env file found", "ERROR")
        if os.path.exists(".env.template"):
            print_status("Found .env.template. Creating .env file...", "INFO")
            subprocess.run(["cp", ".env.template", ".env"])
            print_status("Please edit .env file with your OpenAI API key", "WARNING")
            return False
        else:
            print_status("No .env.template found either", "ERROR")
            return False
    
    print_status(".env file exists", "SUCCESS")
    return True

def validate_api_key():
    """Validate OpenAI API key"""
    print_status("Validating OpenAI API key...")
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print_status("OPENAI_API_KEY not found in .env", "ERROR")
        return False
    
    # Check for common formatting issues
    if "\\n" in api_key or "\n" in api_key:
        print_status("API key contains line breaks - this will cause errors", "ERROR")
        print_status("Fix: Put your API key on a single line in .env", "INFO")
        return False
    
    if " " in api_key:
        print_status("API key contains spaces - this may cause issues", "WARNING")
        
    if not api_key.startswith("sk-"):
        print_status("API key does not start with sk- - invalid format", "ERROR")
        return False
    
    if len(api_key) < 20:
        print_status("API key seems too short", "ERROR")
        return False
    
    if api_key.endswith("YOUR_ACTUAL_API_KEY_HERE"):
        print_status("API key is still the template value", "ERROR")
        print_status("Replace YOUR_ACTUAL_API_KEY_HERE with your real API key", "INFO")
        return False
    
    print_status("API key format looks valid", "SUCCESS")
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print_status("Testing OpenAI API connection...")
    
    try:
        from openai import OpenAI
        load_dotenv()
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print_status("OpenAI API connection successful", "SUCCESS")
        return True
        
    except Exception as e:
        error_msg = str(e).lower()
        
        if "quota" in error_msg or "exceeded" in error_msg:
            print_status("OpenAI quota exceeded", "ERROR")
            print_status("Solution: Add billing/credits at https://platform.openai.com/usage", "INFO")
        elif "invalid" in error_msg and "key" in error_msg:
            print_status("Invalid API key", "ERROR")
            print_status("Solution: Get a new key at https://platform.openai.com/api-keys", "INFO")
        elif "rate" in error_msg and "limit" in error_msg:
            print_status("Rate limit exceeded", "WARNING")
            print_status("Solution: Wait or upgrade your plan", "INFO")
        else:
            print_status(f"OpenAI API error: {str(e)}", "ERROR")
        
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_status("Checking Python dependencies...")
    
    required_packages = ["fastapi", "uvicorn", "streamlit", "openai", "python-dotenv", "PyMuPDF"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
        print_status("Run: pip install -r requirements.txt", "INFO")
        return False
    
    print_status("All required packages are installed", "SUCCESS")
    return True

def main():
    """Main diagnostic function"""
    print("🔍 Smart Document Assistant - Diagnostic Tool")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check .env file
    if not check_env_file():
        all_checks_passed = False
    
    # Validate API key
    if not validate_api_key():
        all_checks_passed = False
    
    # Check dependencies
    if not check_dependencies():
        all_checks_passed = False
    
    # Test OpenAI connection (only if previous checks passed)
    if all_checks_passed:
        if not test_openai_connection():
            all_checks_passed = False
    
    print("\n" + "=" * 50)
    
    if all_checks_passed:
        print_status("All checks passed! Your application should work on the server.", "SUCCESS")
        print_status("Run ./start.sh to start the application", "INFO")
    else:
        print_status("Some issues found. Please fix them before deploying.", "ERROR")
        print_status("Common fixes:", "INFO")
        print("  1. Ensure .env file exists with valid API key")
        print("  2. API key should be on a single line")
        print("  3. Check OpenAI billing at https://platform.openai.com/usage")
        print("  4. Run: pip install -r requirements.txt")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())

