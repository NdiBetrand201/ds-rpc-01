#!/usr/bin/env python3
"""
Data setup script for FinSolve Internal Chatbot
This script initializes the ChromaDB database with company data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.data_ingestion import DataIngestionService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main setup function"""
    logger.info("Starting FinSolve Chatbot data setup...")
    
    try:
        # Initialize data ingestion service
        ingestion_service = DataIngestionService()
        
        # Ingest all data
        ingestion_service.ingest_all_data()
        
        logger.info("Data setup completed successfully!")
        logger.info("You can now start the FastAPI server and Streamlit app.")
        
    except Exception as e:
        logger.error(f"Error during data setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
