function initializeApp() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }

    // Set initial theme based on local storage or system preference
    const savedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

function showSuccessAnimation() {
    const notification = document.getElementById('success-notification');
    if (notification) {
        notification.classList.remove('hidden');
        notification.classList.add('visible');

        setTimeout(() => {
            notification.classList.remove('visible');
            notification.classList.add('hidden');
        }, 3000); // Hide after 3 seconds
    }
}

// Make functions globally accessible (for Streamlit's st.markdown to call them)
window.initializeApp = initializeApp;
window.toggleTheme = toggleTheme;
window.showSuccessAnimation = showSuccessAnimation;

// Ensure theme is applied on initial load based on saved preference
document.addEventListener('DOMContentLoaded', initializeApp);