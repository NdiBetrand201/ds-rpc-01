
import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from app.models.schemas import QueryResponse, Source
from app.services.auth_service import AuthService
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    """
    Retrieval-Augmented Generation (RAG) service using Groq via LangChain with conversation memory.
    """

    def __init__(self):
        self.auth_service = AuthService()
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
        self.memory = {}  # Dictionary to store user-specific conversation history

        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="finsolve_data",
            )
            logger.info("Loaded existing ChromaDB collection 'finsolve_data'")
            if self.collection.count() == 0:
                logger.info("Collection is empty, ingesting data.")
                self._ingest_data()
            else:
                logger.info(f"Collection 'finsolve_data' has {self.collection.count()} items.")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            logger.info("Attempting to create a new ChromaDB collection and ingest data.")
            self.collection = self.chroma_client.create_collection("finsolve_data")
            self._ingest_data()

        # Initialize Groq LLM via LangChain
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            logger.warning("GROQ_API_KEY not found. LLM responses will fall back to rule-based generation.")
            self.groq_model = None
        else:
            self.groq_model = ChatGroq(
                groq_api_key=groq_api_key,
                model_name="llama3-70b-8192",
                temperature=0.0,
                max_tokens=500,
            )
            logger.info("Groq LangChain model initialized.")

    def _ingest_data(self):
        logger.info("Starting data ingestion into ChromaDB...")
        data_mappings = [
            {
                "file_path": "resources/data/engineering/engineering_master_doc.md",
                "department": "Engineering",
                "access_roles": ["engineering", "c-level"]
            },
            {
                "file_path": "resources/data/finance/financial_summary.md",
                "department": "Finance",
                "access_roles": ["finance", "c-level"]
            },
            {
                "file_path": "resources/data/finance/quarterly_financial_report.md",
                "department": "Finance",
                "access_roles": ["finance", "c-level"]
            },
            {
                "file_path": "resources/data/marketing/marketing_report_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"]
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q1_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"]
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q2_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"]
            },
            {
                "file_path": "resources/data/marketing/marketing_report_q3_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"]
            },
            {
                "file_path": "resources/data/marketing/market_report_q4_2024.md",
                "department": "Marketing",
                "access_roles": ["marketing", "c-level"]
            },
            {
                "file_path": "resources/data/general/employee_handbook.md",
                "department": "General",
                "access_roles": ["finance", "marketing", "hr", "engineering", "c-level", "employee"]
            }
        ]

        documents_to_add = []
        metadatas_to_add = []
        ids_to_add = []

        for idx, mapping in enumerate(data_mappings):
            file_path = mapping["file_path"]
            try:
                if not os.path.exists(file_path):
                    logger.warning(f"File not found, skipping: {file_path}")
                    continue

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                chunks = self._split_text(content)

                for chunk_idx, chunk in enumerate(chunks):
                    documents_to_add.append(chunk)
                    metadatas_to_add.append({
                        "department": mapping["department"],
                        "access_roles": ",".join(mapping["access_roles"]),
                        "source_file": os.path.basename(file_path),
                        "chunk_id": f"{idx}_{chunk_idx}",
                        "document_name": os.path.basename(file_path).replace(".md", "").replace("_", " ").title(),
                        "update_date": datetime.now().strftime("%Y-%m-%d")
                    })
                    ids_to_add.append(f"doc_{idx}_chunk_{chunk_idx}")

                logger.info(f"Processed and chunked data from {file_path}")
            except Exception as e:
                logger.error(f"Error processing {file_path} during ingestion: {e}")

        if documents_to_add:
            self.collection.add(
                documents=documents_to_add,
                metadatas=metadatas_to_add,
                ids=ids_to_add
            )
            logger.info(f"Successfully ingested {len(documents_to_add)} document chunks into ChromaDB.")
        else:
            logger.warning("No documents were found or processed for ingestion. ChromaDB collection might be empty.")

    def _split_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
            if i >= len(words) - overlap and len(words[i:]) <= overlap:
                break
        return chunks

    def _retrieve_documents(self, query: str, user_role: str, n_results: int = 5) -> List[Dict]:
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,
                include=["documents", "metadatas", "distances"]
            )

            filtered_results = []
            if results and results["metadatas"] and results["metadatas"][0]:
                for i, metadata in enumerate(results["metadatas"][0]):
                    access_roles_str = metadata.get("access_roles", "")
                    access_roles = access_roles_str.split(",") if access_roles_str else []
                    if user_role in access_roles or "c-level" == user_role:
                        filtered_results.append({
                            "document": results["documents"][0][i],
                            "metadata": metadata,
                            "distance": results["distances"][0][i]
                        })
                    if len(filtered_results) >= n_results:
                        break
            filtered_results.sort(key=lambda x: x["distance"])
            return filtered_results[:n_results]
        except Exception as e:
            logger.error(f"Error retrieving documents from ChromaDB: {e}")
            return []

    def _get_conversation_memory(self, username: str, user_role: str) -> ConversationBufferMemory:
        """
        Initialize or retrieve conversation memory for a user and role.
        """
        memory_key = f"{username}_{user_role}"
        if memory_key not in self.memory:
            self.memory[memory_key] = ConversationBufferMemory(
                memory_key=memory_key,
                input_key="query",
                output_key="response",
                max_token_limit=1000  # Limit to manage token usage
            )
            logger.info(f"Created new conversation memory for {memory_key}")
        return self.memory[memory_key]

    def _generate_response(self, query: str, context_docs: List[Dict], user_role: str, username: str) -> str:
        if not context_docs:
            return "I couldn't find any relevant information to answer your query that you are authorized to access. Please try rephrasing your question or contact your administrator if you believe you should have access to this information."

        # Limit to top 3 context docs, and truncate each to 400 chars
        max_docs = 3
        max_chars_per_doc = 400

        context = "\n\n".join([
            f"Source: {doc['metadata'].get('document_name', doc['metadata']['source_file'])}\nContent: {doc['document'][:max_chars_per_doc]}"
            for doc in context_docs[:max_docs]
        ])

        # Load conversation memory
        memory = self._get_conversation_memory(username, user_role)
        memory_chat_history = memory.load_memory_variables({}).get("history", [])

        if self.groq_model:
            try:
                # Construct prompt with conversation history
                prompt_messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an AI assistant for FinSolve Technologies, a FinTech company. "
                            "Provide helpful, accurate, and concise responses based *only* on the provided context. "
                            "If the information is not in the context, state that explicitly. "
                            "Always cite the document names from the context when referencing information. "
                            "Use the conversation history to maintain context for follow-up questions. "
                            "Keep responses to a maximum of 4 lines."
                        )
                    },
                    {"role": "user", "content": f"Conversation History:\n{memory_chat_history}\n\nUser Role: {user_role}\nUser Query: {query}\n\nContext from company documents:\n{context}\n\nResponse:"}
                ]
                result = self.groq_model.invoke(prompt_messages)
                response = result.content.strip() if hasattr(result, "content") else str(result)

                # Save to memory
                memory.save_context(
                    inputs={"query": query},
                    outputs={"response": response}
                )
                logger.info(f"Saved query and response to memory for {username} ({user_role})")
                return response
            except Exception as e:
                logger.error(f"Groq API error during response generation: {e}")
                return self._generate_fallback_response(query, context_docs, user_role)
        else:
            return self._generate_fallback_response(query, context_docs, user_role)

    def _generate_fallback_response(self, query: str, context_docs: List[Dict], user_role: str) -> str:
        query_lower = query.lower()
        source_names = [doc["metadata"].get("document_name", doc["metadata"]["source_file"]) for doc in context_docs]
        if any(word in query_lower for word in ["revenue", "income", "profit", "financial", "q4"]):
            return (f"Based on financial documents (e.g., {', '.join(source_names) if source_names else 'relevant reports'}) "
                    f"available to your role ({user_role}), FinSolve's financial performance metrics are detailed in those sources. "
                    "Please consult the relevant financial reports for specific figures and analysis.")
        elif any(word in query_lower for word in ["marketing", "campaign", "customer", "acquisition", "sales"]):
            return (f"According to marketing reports (e.g., {', '.join(source_names) if source_names else 'marketing reports'}) "
                    f"accessible to your role ({user_role}), FinSolve has been running various marketing campaigns focused on "
                    "customer acquisition and brand awareness. Detailed performance metrics are available in the source documents.")
        elif any(word in query_lower for word in ["employee", "hr", "policy", "handbook", "leave", "benefits"]):
            return (f"The employee handbook and HR policies (e.g., {', '.join(source_names) if source_names else 'HR documents'}) "
                    f"contain information relevant to your query. As a {user_role} user, you have access to policies regarding "
                    "work procedures, benefits, and company guidelines. Please refer to these documents for specific details.")
        elif any(word in query_lower for word in ["engineering", "technical", "architecture", "system", "sdlc", "security", "roadmap"]):
            return (f"The engineering documentation (e.g., {', '.join(source_names) if source_names else 'technical documents'}) "
                    f"provides technical information about FinSolve's systems and architecture. Based on your role ({user_role}), "
                    "I can provide information about technical specifications, development practices, and security measures. "
                    "Consult the relevant engineering documents for in-depth understanding.")
        else:
            return (f"I found some relevant document(s) (e.g., {', '.join(source_names) if source_names else 'some documents'}) related to your query. "
                    f"Based on your role as {user_role}, you have access to information from these sources. "
                    "For detailed information, please refer directly to the source documents.")

    def process_query(self, query: str, user_role: str, username: str, context: Optional[str] = None) -> QueryResponse:
        logger.info(f"RAGService: Processing query for user {username} (role: {user_role}): {query}")
        relevant_docs = self._retrieve_documents(query, user_role)
        logger.info(f"RAGService: Found {len(relevant_docs)} accessible and relevant documents for '{query}'.")
        response_text = self._generate_response(query, relevant_docs, user_role, username)
        sources = []
        for doc in relevant_docs:
            relevance = max(0.0, 1.0 - (doc["distance"] / 1.5))
            sources.append(Source(
                document=doc["metadata"].get("document_name", doc["metadata"]["source_file"]),
                department=doc["metadata"]["department"],
                update_date=doc["metadata"].get("update_date", datetime.now().strftime("%Y-%m-%d")),
                relevance_score=relevance
            ))
        return QueryResponse(
            response=response_text,
            sources=sources,
            user_role=user_role,
            timestamp=datetime.utcnow(),
            query_processed=query
        )

    def clear_memory(self, username: str, user_role: str) -> None:
        """
        Clear conversation memory for a specific user and role.
        """
        memory_key = f"{username}_{user_role}"
        if memory_key in self.memory:
            del self.memory[memory_key]
            logger.info(f"Cleared conversation memory for {memory_key}")
        else:
            logger.info(f"No conversation memory found for {memory_key}")