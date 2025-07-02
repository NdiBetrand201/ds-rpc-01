import os
import logging
from typing import List, Dict
import time
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionService:
    """Service for ingesting data into ChromaDB"""

    def __init__(self):
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        # If chromadb supports timeout, set it here (pseudo-code, adjust as needed)
        # self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db", timeout=60)
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db",settings=Settings(chroma_sysdb_request_timeout_seconds=600))

    def ingest_all_data(self):
        """Ingest all data files into ChromaDB"""
        logger.info("Starting data ingestion process...")

        # Create or get collection
        try:
            collection = self.chroma_client.get_collection("finsolve_data")
            # Clear existing data
            collection.delete()
            logger.info("Cleared existing collection")
        except Exception as e:
            logger.warning(f"Collection not found or could not be cleared: {e}")

        try:
            collection = self.chroma_client.create_collection("finsolve_data")
        except Exception as e:
            logger.warning(f"Collection already exists, getting existing one: {e}")
            collection = self.chroma_client.get_collection("finsolve_data")

        # Define data mappings
        data_mappings = [
            {
                "file_path": "resources/data/engineering/engineering_master_doc.md",
                "department": "Engineering",
                "access_roles": ["engineering", "c-level"],
                "data_type": "technical_documentation"
            },
            {
                "file_path": "resources/data/finance/financial_summary.md",
                "department": "Finance",
                "access_roles": ["finance", "c-level"],
                "data_type": "financial_reports"
            },
            {
                "file_path": "resources/data/finance/quarterly_financial_report.md",
                "department": "Finance",
                "access_roles": ["finance", "c-level"],
                "data_type": "financial_reports"
            },
            {
                "file_path": "resources/data/marketing/marketing_report_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"],
                "data_type": "marketing_reports"
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q1_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"],
                "data_type": "marketing_reports"
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q2_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"],
                "data_type": "marketing_reports"
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q3_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"],
                "data_type": "marketing_reports"
            },
            {
                "file_path": "resources/data/marketing/market_report_q4_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"],
                "data_type": "marketing_reports"
            },
            {
                "file_path": "resources/data/general/employee_handbook.md",
                "department": "General",
                "access_roles": ["finance", "marketing", "hr", "engineering", "c-level", "employee"],
                "data_type": "policies_handbook"
            }
        ]

        # Process HR CSV data
        self._process_hr_data(collection)

        # Process markdown files
        documents = []
        metadatas = []
        ids = []

        for idx, mapping in enumerate(data_mappings):
            try:
                if os.path.exists(mapping["file_path"]):
                    with open(mapping["file_path"], 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Split content into chunks
                    chunks = self._split_text(content)

                    for chunk_idx, chunk in enumerate(chunks):
                        documents.append(chunk)
                        metadatas.append({
                            "department": mapping["department"],
                            "access_roles": ",".join(mapping["access_roles"]),
                            "source_file": os.path.basename(mapping["file_path"]),
                            "data_type": mapping["data_type"],
                            "chunk_id": f"{idx}_{chunk_idx}",
                            "update_date": "2024-12-01"
                        })
                        ids.append(f"doc_{idx}_chunk_{chunk_idx}")

                logger.info(f"Processed {mapping['file_path']}")
            except Exception as e:
                logger.error(f"Error processing {mapping['file_path']}: {e}")

        if documents:
            # Add documents to ChromaDB in batches with retry logic
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                for attempt in range(3):
                    try:
                        collection.add(
                            documents=batch_docs,
                            metadatas=batch_metas,
                            ids=batch_ids
                        )
                        break  # Success, exit retry loop
                    except Exception as e:
                        logger.error(f"Error adding batch {i//batch_size+1}: {e}")
                        if attempt < 2:
                            logger.info("Retrying in 10 seconds...")
                            time.sleep(10)
                        else:
                            logger.error("Max retries reached for this batch.")
            logger.info(f"Successfully ingested {len(documents)} document chunks into ChromaDB")
        else:
            logger.warning("No documents were ingested")

    def _process_hr_data(self, collection):
        """Process HR CSV data and add to collection"""
        try:
            import pandas as pd
            hr_file = "resources/data/hr/hr_data.csv"

            if os.path.exists(hr_file):
                df = pd.read_csv(hr_file)

                # Create summary documents from HR data
                hr_summary = f"""
                HR Data Summary:
                Total Employees: {len(df)}
                Departments: {', '.join(df['department'].unique())}
                Locations: {', '.join(df['location'].unique())}
                Average Salary: ${df['salary'].mean():.2f}
                Average Performance Rating: {df['performance_rating'].mean():.2f}
                Average Attendance: {df['attendance_pct'].mean():.2f}%
                """

                # Retry logic for HR data add
                for attempt in range(3):
                    try:
                        collection.add(
                            documents=[hr_summary],
                            metadatas=[{
                                "department": "HR",
                                "access_roles": "hr,c-level",
                                "source_file": "hr_data.csv",
                                "data_type": "hr_analytics",
                                "chunk_id": "hr_summary",
                                "update_date": "2024-12-01"
                            }],
                            ids=["hr_summary_001"]
                        )
                        logger.info("Processed HR data successfully")
                        break
                    except Exception as e:
                        logger.error(f"Error processing HR data (attempt {attempt+1}): {e}")
                        if attempt < 2:
                            logger.info("Retrying in 10 seconds...")
                            time.sleep(10)
                        else:
                            logger.error("Max retries reached for HR data.")
        except Exception as e:
            logger.error(f"Error processing HR data: {e}")

    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)

            if i + chunk_size >= len(words):
                break

        return chunks

if __name__ == "__main__":
    ingestion_service = DataIngestionService()
    ingestion_service.ingest_all_data()
