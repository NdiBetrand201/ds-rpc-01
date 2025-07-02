import streamlit as st
import requests
import json
import os
from pathlib import Path
import time
from datetime import datetime

# Set page configuration with modern layout and FinSolve branding
st.set_page_config(
    page_title="FinSolve AI Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS and JavaScript
css_path = Path("styles.css")
if css_path.exists():
    with open(css_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

js_path = Path("scripts.js")
if js_path.exists():
    with open(js_path, "r") as f:
        st.markdown(f"""
            <script>{f.read()}</script>
            <script>
                // Initialize application
                document.addEventListener('DOMContentLoaded', function() {{
                    initializeApp();
                }});
            </script>
        """, unsafe_allow_html=True)

# API base URL
API_URL = "http://localhost:8000"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "accessible_data" not in st.session_state:
    st.session_state.accessible_data = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# Enhanced query suggestions with icons
SUGGESTIONS = {
    "finance": [
        {"text": "Q1 2024 Revenue Analysis", "icon": "📊"},
        {"text": "Budget Performance Review", "icon": "💰"},
        {"text": "Cost Optimization Insights", "icon": "📈"}
    ],
    "marketing": [
        {"text": "Campaign ROI Analysis", "icon": "🎯"},
        {"text": "Customer Acquisition Metrics", "icon": "👥"},
        {"text": "Brand Performance Report", "icon": "🚀"}
    ],
    "hr": [
        {"text": "Employee Satisfaction Survey", "icon": "😊"},
        {"text": "Recruitment Pipeline Status", "icon": "🔍"},
        {"text": "Performance Review Insights", "icon": "⭐"}
    ],
    "engineering": [
        {"text": "System Performance Metrics", "icon": "⚡"},
        {"text": "Security Compliance Status", "icon": "🔒"},
        {"text": "Technical Debt Analysis", "icon": "🔧"}
    ],
    "c-level": [
        {"text": "Company-wide KPI Dashboard", "icon": "📋"},
        {"text": "Strategic Growth Opportunities", "icon": "🎯"},
        {"text": "Cross-department Synergies", "icon": "🤝"}
    ],
    "employee": [
        {"text": "Employee Handbook", "icon": "📖"},
        {"text": "Company Policies", "icon": "📋"},
        {"text": "Benefits Information", "icon": "🎁"}
    ]
}

# Role colors for better visual distinction
ROLE_COLORS = {
    "finance": "#4CAF50",
    "marketing": "#FF6B6B",
    "hr": "#4ECDC4",
    "engineering": "#45B7D1",
    "c-level": "#9B59B6",
    "employee": "#95A5A6"
}

# Helper functions
def login(username: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{API_URL}/login",
            auth=(username, password)
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = data["username"]
            st.session_state.role = data["role"]
            get_accessible_data()
            return True
        else:
            st.error(f"🚫 Login failed: {response.json().get('detail', 'Unknown error')}")
            return False
    except requests.RequestException as e:
        st.error(f"🔌 Cannot connect to API. Please check if the server is running.")
        return False

def get_accessible_data():
    if st.session_state.token:
        try:
            response = requests.get(
                f"{API_URL}/user/accessible-data",
                headers={"Authorization": f"Bearer {st.session_state.token}"}
            )
            if response.status_code == 200:
                st.session_state.accessible_data = response.json().get("accessible_data", [])
            else:
                st.error("❌ Failed to fetch accessible data")
        except requests.RequestException as e:
            st.error(f"⚠️ Error fetching accessible data: {str(e)}")

def add_user(username: str, password: str, role: str):
    if st.session_state.token and st.session_state.role == "c-level":
        try:
            response = requests.post(
                f"{API_URL}/add-user",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                json={"username": username, "password": password, "role": role}
            )
            if response.status_code == 200:
                st.success("✅ " + response.json().get("message"))
            else:
                st.error("❌ " + response.json().get("detail", "Failed to add user"))
        except requests.RequestException as e:
            st.error(f"⚠️ Error adding user: {str(e)}")
    else:
        st.error("🔐 Only C-level users can add new users")

def send_chat_query(query: str, context: str = ""):
    if st.session_state.token:
        try:
            response = requests.post(
                f"{API_URL}/chat",
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                json={"query": query, "context": context}
            )
            if response.status_code == 200:
                data = response.json()
                sources = data.get("sources", [])
                formatted_sources = [
                    f"{source['document']} ({source.get('department', 'Unknown')})"
                    for source in sources
                    if isinstance(source, dict) and 'document' in source
                ]
                
                # Add timestamp
                timestamp = datetime.now().strftime("%H:%M")
                
                # Add user query to chat history
                st.session_state.chat_history.append({
                    "sender": "user",
                    "message": query,
                    "timestamp": timestamp
                })

                # Add AI response to chat history
                st.session_state.chat_history.append({
                    "sender": "ai",
                    "message": data["response"],
                    "sources": formatted_sources,
                    "timestamp": timestamp
                })
                
                # Trigger success animation
                st.markdown("""
                    <script>
                        if (typeof showSuccessAnimation === 'function') {
                            showSuccessAnimation();
                        }
                    </script>
                """, unsafe_allow_html=True)
                
            else:
                st.error("❌ " + response.json().get("detail", "Chat query failed"))
        except requests.RequestException as e:
            st.error(f"⚠️ Error sending query: {str(e)}")

# Enhanced sidebar with animations
with st.sidebar:
    # Logo and branding
    st.markdown("""
        <div class="logo-container">
            <div class="logo-circle">
                <span class="logo-text">FS</span>
            </div>
            <h2 class="brand-title">FinSolve AI</h2>
            <p class="brand-subtitle">Your Intelligent Business Assistant</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Theme toggle
    st.markdown("""
        <div class="theme-toggle-container">
            <button id="theme-toggle" class="theme-toggle-btn" onclick="toggleTheme()">
                <span class="theme-icon">🌓</span>
                <span class="theme-text">Toggle Theme</span>
            </button>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-divider'></div>", unsafe_allow_html=True)
    
    if st.session_state.token:
        # User profile section
        role_color = ROLE_COLORS.get(st.session_state.role, "#95A5A6")
        st.markdown(f"""
            <div class="user-profile">
                <div class="user-avatar" style="background: linear-gradient(135deg, {role_color}, {role_color}CC);">
                    {st.session_state.username[0].upper()}
                </div>
                <div class="user-details">
                    <h3 class="user-name">{st.session_state.username}</h3>
                    <span class="user-role" style="color: {role_color};">{st.session_state.role.title()}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        st.markdown(f"""
            <div class="quick-stats">
                <div class="stat-item">
                    <span class="stat-number">{len(st.session_state.chat_history) // 2 if st.session_state.chat_history else 0}</span>
                    <span class="stat-label">Queries</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{len(st.session_state.accessible_data)}</span>
                    <span class="stat-label">Data Sources</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key="logout", help="Sign out securely", use_container_width=True):
            st.session_state.token = None
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.accessible_data = []
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.markdown("""
            <div class="login-prompt">
                <div class="login-icon">🔐</div>
                <p>Please sign in to access your personalized AI assistant</p>
            </div>
        """, unsafe_allow_html=True)

# Main content area
if not st.session_state.token:
    # Enhanced login page
    st.markdown("""
        <div class="login-container">
            <div class="login-hero">
                <h1 class="login-title">Welcome to FinSolve AI</h1>
                <p class="login-subtitle">Unlock intelligent insights for your business</p>
                <div class="feature-pills">
                    <span class="pill">🤖 AI-Powered</span>
                    <span class="pill">🔒 Secure</span>
                    <span class="pill">⚡ Fast</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<h3 class="form-title">Sign In</h3>', unsafe_allow_html=True)
            username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_password")
            
            col_a, col_b = st.columns([1, 1])
            with col_a:
                remember = st.checkbox("Remember me", key="remember")
            with col_b:
                st.markdown('<p class="forgot-link"><a href="#">Forgot password?</a></p>', unsafe_allow_html=True)
            
            submit = st.form_submit_button("🚀 Sign In", use_container_width=True)
            if submit and username and password:
                with st.spinner("Authenticating..."):
                    if login(username, password):
                        st.success("✅ Login successful!")
                        time.sleep(1)
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # Main dashboard
    st.markdown(f"""
        <div class="dashboard-header">
            <h1 class="dashboard-title">Welcome back, {st.session_state.username}! 👋</h1>
            <p class="dashboard-subtitle">What would you like to explore today?</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Enhanced tabs with icons
    tab1, tab2, tab3, tab4 = st.tabs(["💬 Chat Assistant", "📊 Data Access", "👥 User Management", "📈 Analytics"])
    
    with tab1:
        # Quick actions row
        suggestions = SUGGESTIONS.get(st.session_state.role, [])
        if suggestions:
            st.markdown('<div class="suggestions-container">', unsafe_allow_html=True)
            st.markdown('<h4 class="suggestions-title">✨ Quick Actions</h4>', unsafe_allow_html=True)
            
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(
                        f"{suggestion['icon']} {suggestion['text']}", 
                        key=f"suggestion_{i}",
                        use_container_width=True,
                        help=f"Click to ask: {suggestion['text']}"
                    ):
                        send_chat_query(suggestion['text'])
                        st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat interface
        st.markdown('<div class="chat-interface">', unsafe_allow_html=True)
        
        # Chat history with enhanced design
        # Display chat history first so the latest messages are at the bottom and visible when scrolled
        if st.session_state.chat_history:
            st.markdown('<div class="chat-history">', unsafe_allow_html=True)
            st.markdown('<h4 class="history-title">💬 Conversation History</h4>', unsafe_allow_html=True)
            
            for entry in st.session_state.chat_history:
                timestamp = entry.get('timestamp', '')
                if entry['sender'] == 'user':
                    st.markdown(f"""
                        <div class="message-container user-container">
                            <div class="message user-message">
                                <div class="message-header">
                                    <span class="message-author">You</span>
                                    <span class="message-time">{timestamp}</span>
                                </div>
                                <div class="message-content">{entry['message']}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    sources_html = ""
                    if entry.get('sources'):
                        sources_html = f'<div class="message-sources">📚 Sources: {", ".join(entry["sources"])}</div>'
                    st.markdown(f"""
                        <div class="message-container ai-container">
                            <div class="message ai-message">
                                <div class="message-header">
                                    <span class="message-author">🤖 FinSolve AI</span>
                                    <span class="message-time">{timestamp}</span>
                                </div>
                                <div class="message-content">{entry['message']}</div>
                                {sources_html}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                query = st.text_input(
                    "💭 Your Question", 
                    placeholder="Ask me anything about your business data...", 
                    key="chat_input",
                    label_visibility="collapsed"
                )
            with col2:
                submit_chat = st.form_submit_button("🚀 Ask", use_container_width=True)
            
            context = st.text_area(
                "📝 Additional Context (Optional)", 
                placeholder="Provide any relevant context to get better answers...", 
                key="chat_context",
                height=80
            )
            
            if submit_chat and query:
                with st.spinner("🤔 Thinking..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(i + 1)
                    send_chat_query(query, context)
                    progress_bar.empty()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="data-access-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📊 Your Data Access</h3>', unsafe_allow_html=True)
        
        if st.session_state.accessible_data:
            # Create a grid layout for departments
            cols = st.columns(3)
            for i, dept in enumerate(st.session_state.accessible_data):
                with cols[i % 3]:
                    dept_color = ROLE_COLORS.get(dept.lower(), "#95A5A6")
                    st.markdown(f"""
                        <div class="dept-card" style="border-left: 4px solid {dept_color};">
                            <div class="dept-icon">🏢</div>
                            <div class="dept-name">{dept.title()}</div>
                            <div class="dept-status">✅ Active</div>
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <h4>No Data Access</h4>
                    <p>Contact your administrator to request access to data sources.</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        if st.session_state.role == "c-level":
            st.markdown('<div class="user-management-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="section-title">👥 User Management</h3>', unsafe_allow_html=True)
            
            with st.form("add_user_form"):
                st.markdown('<h4 class="form-subtitle">➕ Add New User</h4>', unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("👤 Username", placeholder="Enter username", key="new_username")
                    new_password = st.text_input("🔑 Password", type="password", placeholder="Enter secure password", key="new_password")
                with col2:
                    new_role = st.selectbox(
                        "🎭 Role", 
                        ["finance", "marketing", "hr", "engineering", "c-level", "employee"], 
                        key="new_role"
                    )
                    st.markdown('<div class="role-description">', unsafe_allow_html=True)
                    if new_role:
                        role_descriptions = {
                            "finance": "Access to financial data and reports",
                            "marketing": "Access to marketing campaigns and metrics",
                            "hr": "Access to HR policies and employee data",
                            "engineering": "Access to technical documentation",
                            "c-level": "Full system access and user management",
                            "employee": "Basic access to company policies"
                        }
                        st.info(f"ℹ️ {role_descriptions.get(new_role, 'Standard employee access')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                submit_user = st.form_submit_button("➕ Create User", use_container_width=True)
                if submit_user and new_username and new_password:
                    add_user(new_username, new_password, new_role)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="access-denied">
                    <div class="denied-icon">🔐</div>
                    <h4>Access Restricted</h4>
                    <p>User management is only available to C-level executives.</p>
                </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="analytics-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📈 Usage Analytics</h3>', unsafe_allow_html=True)
        
        # Mock analytics data - replace with real data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Queries", len(st.session_state.chat_history) // 2 if st.session_state.chat_history else 0, delta="↗️ +12%")
        with col2:
            st.metric("Data Sources", len(st.session_state.accessible_data), delta="→ 0%")
        with col3:
            st.metric("Avg Response Time", "1.2s", delta="↘️ -0.3s")
        with col4:
            st.metric("Satisfaction", "98%", delta="↗️ +2%")
        
        # Simple chart placeholder
        if st.session_state.chat_history:
            st.markdown('<h4 class="chart-title">📊 Query Trends</h4>', unsafe_allow_html=True)
            # This would be replaced with actual chart data
            st.info("📈 Analytics dashboard will be enhanced with real-time data visualization.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Success notification container
st.markdown('<div id="success-notification" class="success-notification hidden">✅ Query processed successfully!</div>', unsafe_allow_html=True)