# import os
# from langchain_community.document_loaders import TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import Chroma
# from langchain_huggingface import HuggingFaceEmbeddings
# import transformers

# # Increase timeout for Hugging Face downloads
# transformers.hf_api.HF_HUB_REQUEST_TIMEOUT = 3000  # Set timeout to 30 seconds

# # Define dataset metadata with folder paths
# DATASETS = [
#     {
#         "folder": "engineering",
#         "file": "engineering_master_doc.md",
#         "department": "Engineering",
#         "access": ["Engineering", "C-Level"],
#         "update_date": "2024-03-31"
#     },
#     {
#         "folder": "finance",
#         "file": "finance.md",
#         "department": "Finance",
#         "access": ["Finance", "C-Level"],
#         "update_date": "2024-03-31"
#     },
#     {
#         "folder": "hr",
#         "file": "hr.md",
#         "department": "HR",
#         "access": ["HR", "C-Level"],
#         "update_date": "2024-09-30"
#     },
#     {
#         "folder": "marketing",
#         "file": "marketing.md",
#         "department": "Marketing",
#         "access": ["Marketing", "C-Level"],
#         "update_date": "2024-03-31"
#     },
#     {
#         "folder": "handbook",
#         "file": "handbook.md",
#         "department": "General",
#         "access": ["Finance", "Marketing", "HR", "Engineering", "C-Level", "Employee"],
#         "update_date": "2024-01-01"
#     }
# ]

# # Initialize embeddings
# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2",
#     model_kwargs={"device": "cpu"},  # Use CPU for simplicity; adjust to GPU if available
#     encode_kwargs={"normalize_embeddings": True}
# )

# # Initialize text splitter
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=500,
#     chunk_overlap=50,
#     length_function=lambda text: len(text.split())
# )

# # Load and ingest datasets
# def ingest_data():
#     documents = []
#     data_dir = "data"
    
#     for dataset in DATASETS:
#         file_path = os.path.join(data_dir, dataset["folder"], dataset["file"])
#         if not os.path.exists(file_path):
#             print(f"Warning: {file_path} not found, skipping.")
#             continue
            
#         # Load Markdown file
#         loader = TextLoader(file_path)
#         raw_docs = loader.load()
        
#         # Split into chunks
#         chunks = text_splitter.split_documents(raw_docs)
        
#         # Add metadata to each chunk
#         for chunk in chunks:
#             chunk.metadata = {
#                 "department": dataset["department"],
#                 "access": dataset["access"],
#                 "update_date": dataset["update_date"],
#                 "source": f"{dataset['folder']}/{dataset['file']}"
#             }
#         documents.extend(chunks)
    
#     # Store in ChromaDB
#     chroma = Chroma.from_documents(
#         documents=documents,
#         embedding=embeddings,
#         collection_name="finsolve_data",
#         persist_directory="data/chroma_db"
#     )
#     chroma.persist()
#     print(f"Ingested {len(documents)} chunks into ChromaDB.")

# if __name__ == "__main__":
#     ingest_data()
