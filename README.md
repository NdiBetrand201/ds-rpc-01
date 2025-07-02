FinSolve Internal Chatbot with Role-Based Access Control
A sophisticated RAG (Retrieval-Augmented Generation) chatbot system designed for FinSolve Technologies, featuring SQLite-based authentication, conversation memory, role-based access control, and a modern Streamlit frontend with intelligent document retrieval.
🏗️ System Architecture
[Streamlit UI (Dark Mode, Animations, AI Suggestions)] ←→ [FastAPI Backend]
                      ├── [SQLite Authentication]
                      ├── [JWT Authentication]
                      ├── [Role-Based Access Control]
                      ├── [RAG Pipeline with Conversation Memory]
                      └── [ChromaDB Vector Store]

🎯 Features

🔐 Secure Authentication: SQLite-based user management with bcrypt password hashing and JWT tokens.
👥 Role-Based Access Control (RBAC): Six roles with granular data permissions.
🤖 Intelligent RAG Pipeline: Context-aware responses using ChromaDB, embeddings, and ConversationBufferMemory for conversation history.
📊 Rich Data Sources: Engineering, Finance, Marketing, HR, and General company data.
💬 Modern Chat Interface: Streamlit frontend with dark mode, micro-animations, AI-driven query suggestions, progress bar, and accessibility features.
🔍 Source Attribution: Responses include source references from retrieved documents.
⚡ Real-time Processing: Fast query processing with async FastAPI endpoints.
👤 User Management: C-level users can add new users via the /add-user endpoint and UI.
📱 Responsive Design: Mobile-first Streamlit UI with persistent chat history via localStorage.

👥 User Roles & Permissions



Role
Access
Purpose



Finance
Financial reports, marketing expenses, equipment costs
Financial planning, audits, investor reporting


Marketing
Campaign performance, customer feedback, sales metrics
Campaign planning, budget allocation, performance reviews


HR
Employee data, attendance, payroll, performance reviews
Talent forecasting, compliance reporting, employee engagement


Engineering
Technical architecture, CI/CD pipelines, security models
System maintenance, audits, onboarding, scaling


C-Level
Full access to all company data, user management
Strategic decision-making, cross-departmental oversight, user administration


Employee
General company information, employee handbook
Orientation, policy clarification, general inquiries


🚀 Quick Start
Prerequisites

Python 3.8+
pip package manager
SQLite (included with Python)

Installation

Clone the repository
git clone https://github.com/codebasics/ds-rpc-01
cd dsrpc01


Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux


Install dependencies
pip install -r requirements.txt


Set up the database

SQLite database (data/users.db) is automatically initialized by AuthService with demo users.
ChromaDB is set up by RAGService in data/chroma_db/.
Run data ingestion:python scripts/setup_data.py




Start the services
python scripts/start_services.py

Or start separately:
# Terminal 1: Start FastAPI backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start Streamlit frontend
streamlit run app.py --server.port 8501


Access the application

Streamlit UI: http://localhost:8501
FastAPI API: http://localhost:8000
API Documentation: http://localhost:8000/docs



🔑 Demo Credentials



Username
Password
Role



peter
finance123
Finance


jane
marketing456
Marketing


natasha
hr789
HR


tony
exec2023
C-Level


sam
eng456
Engineering


employee
employee123
Employee


💡 Sample Queries by Role
Finance Team

"What was our Q1 2024 revenue?"
"Show me the marketing expenses breakdown"
"Follow up: What are the key financial risks?"

Marketing Team

"How did our Q2 campaigns perform?"
"What was the customer acquisition cost?"
"Follow up: Show me the ROI for digital marketing"

HR Team

"What are the leave policies?"
"Show me employee performance trends"
"Follow up: What benefits do we offer?"

Engineering Team

"What's our system architecture?"
"Explain our CI/CD pipeline"
"Follow up: What security measures do we have?"

C-Level Executives

"Give me a company overview"
"What are our growth metrics?"
"Follow up: Show me cross-departmental insights"

Employees

"What are the company policies?"
"How do I request leave?"
"Follow up: What training programs are available?"

🏗️ Project Structure
dsrpc01/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── auth_service.py     # SQLite-based authentication & authorization
│   │   ├── rag_service.py      # RAG pipeline with conversation memory
│   │   └── data_ingestion.py   # Data ingestion service
│   └── utils/
│       └── helpers.py          # Utility functions
├── static/
│   ├── styles.css              # Custom CSS for Streamlit
│   ├── scripts.js              # Custom JavaScript for dark mode and persistence
│   ├── finsolve_logo.png       # FinSolve logo
├── data/
│   ├── users.db               # SQLite user database
│   ├── chroma_db/             # ChromaDB vector store
│   └── resources/             # Company data files
│       ├── engineering/
│       ├── finance/
│       ├── marketing/
│       ├── hr/
│       └── general/
├── scripts/
│   ├── setup_data.py          # Database initialization
│   └── start_services.py      # Service startup script
├── app.py                     # Streamlit frontend
├── requirements.txt           # Python dependencies
└── README.md                  # This file

🔧 Configuration
Environment Variables
Create a .env file in the root directory:
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
GROQ_API_KEY=your-groq-api-key

Database Configuration

SQLite: data/users.db is automatically created by AuthService with demo users.
ChromaDB: Vector store in data/chroma_db/ is initialized by RAGService via setup_data.py.

🛠️ API Endpoints



Endpoint
Method
Description
Authentication



/
GET
Root endpoint
None


/login
POST
User authentication
Basic Auth


/add-user
POST
Add new user (c-level only)
Bearer Token (JWT)


/chat
POST
Process chat queries with memory
Bearer Token (JWT)


/user/accessible-data
GET
Get user's data access
Bearer Token (JWT)


/health
GET
Health check
None


🔒 Security Features

SQLite Authentication: Persistent user storage with bcrypt password hashing.
JWT Token Authentication: Secure token-based access for protected endpoints.
Role-Based Access Control: Granular permissions enforced by AuthService.
Data Filtering: RAGService filters responses based on user role.
Secure Headers: CORS restricted to http://localhost:8501 in development.

🚀 Advanced Features
Conversation Memory

Uses ConversationBufferMemory in RAGService to maintain context for follow-up queries.
Example:User: "Show me Q1 2024 revenue"
Bot: "Q1 2024 revenue was $5.3M (Source: financial_summary.md)"
User: "Tell me more about financial performance"
Bot: "Following your question about Q1 revenue, key performance metrics include..." (uses memory)



AI-Driven Query Suggestions

Role-based query suggestions in Streamlit UI (e.g., “Q1 2024 revenue” for Finance users).

Source Attribution

Responses include source metadata:Response: "The marketing spend in Q2 2024 was $2.5M..."
Sources:
📄 marketing_report_q2_2024.md
🏢 Department: Marketing
📅 Updated: 2024-06-30



Modern UI

Dark mode, micro-animations, responsive design, and accessibility (ARIA labels, keyboard navigation).
Chat history persists via browser localStorage.

User Management

C-level users can add new users via /add-user endpoint and Streamlit UI.

🧪 Testing
Manual Testing

Start services: python scripts/start_services.py.
Login with demo credentials (e.g., peter:finance123).
Test role-specific queries and follow-up questions to verify memory.
Test user creation as tony:exec2023.
Verify RBAC (e.g., jane:marketing456 cannot access Finance data).

API Testing

Use FastAPI docs at http://localhost:8000/docs to test endpoints.
Example:curl -X POST "http://localhost:8000/login" -u "peter:finance123"
curl -X POST "http://localhost:8000/chat" -H "Authorization: Bearer <token>" -d '{"query": "Q1 2024 revenue"}'



📈 Performance Optimization

Chunked Document Processing: Efficient text splitting in RAGService.
Async Operations: FastAPI async endpoints for concurrency.
Vector Search: Optimized similarity search with ChromaDB.
Memory Management: ConversationBufferMemory ensures efficient context handling.

🔮 Future Enhancements

Voice Input: Add Web Speech API for accessibility.
Advanced Analytics: Dashboard with charts for query trends.
Multi-modal Input: Support for file uploads and image analysis.
Mobile App: Flutter-based mobile interface.
Caching: Redis for query caching (partially implemented).

🐛 Troubleshooting
Common Issues

ModuleNotFoundError: No module named 'passlib'
pip install passlib[bcrypt]


ChromaDB Connection Error
rm -rf ./data/chroma_db/
python scripts/setup_data.py


Port Already in Use
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9


Backend Connection Error

Ensure FastAPI is running: uvicorn app.main:app --port 8000.
Check API_URL in app.py matches http://localhost:8000.



Logs and Debugging

FastAPI logs: Terminal output from uvicorn.
Streamlit logs: Terminal output from streamlit run app.py.
AuthService logs: Check for “Authentication failed” messages.

🤝 Contributing

Fork the repository.
Create a feature branch: git checkout -b feature/amazing-feature.
Commit changes: git commit -m 'Add some amazing feature'.
Push: git push origin feature/amazing-feature.
Open a Pull Request.

📄 License
MIT License - see the LICENSE file for details.
🙏 Acknowledgments

FinSolve Technologies for project requirements.
ChromaDB for vector database.
Streamlit for modern frontend framework.
FastAPI for high-performance backend.
LangChain for RAG and conversation memory.


Built with ❤️ for FinSolve Technologies
For support, contact the development team or create an issue in the repository.