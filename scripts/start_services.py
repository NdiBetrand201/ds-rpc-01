#!/usr/bin/env python3
"""
Service startup script for FinSolve Internal Chatbot
This script starts both the FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import time
import os
from threading import Thread

def start_fastapi():
    """Start FastAPI server"""
    print("Starting FastAPI server...")
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def start_streamlit():
    """Start Streamlit app"""
    print("Starting Streamlit app...")
    time.sleep(3)  # Wait for FastAPI to start
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/streamlit_app.py", "--server.port", "8501"])

def main():
    """Main function to start both services"""
    print("🚀 Starting FinSolve Internal Chatbot Services...")
    
    # Start FastAPI in a separate thread
    fastapi_thread = Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Streamlit in main thread
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        sys.exit(0)

if __name__ == "__main__":
    main()
