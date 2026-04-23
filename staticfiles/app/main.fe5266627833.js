/**
 * HomeoCompare Main JS - Advanced Features & Shared Logic
 */

const MainApp = {
    init() {
        this.initTheme();
        this.initSidebar();
        this.initMobileMenu();
        this.initParticles();
        this.initClock();
    },

    initTheme() {
        const themeToggle = document.getElementById('themeToggle');
        if (!themeToggle) return;

        const init = () => {
            const theme = localStorage.getItem('theme') || 'dark';
            if (theme === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
        };

        themeToggle.addEventListener('click', () => {
            const isLight = document.documentElement.getAttribute('data-theme') === 'light';
            const next = isLight ? 'dark' : 'light';
            
            if (next === 'light') {
                document.documentElement.setAttribute('data-theme', 'light');
            } else {
                document.documentElement.removeAttribute('data-theme');
            }
            localStorage.setItem('theme', next);
        });

        init();
    },

    updateThemeBtn(theme) {
        // No longer needed, handled beautifully by CSS!
    },

    initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const hamburger = document.getElementById('hamburgerBtn');
        const closeBtn = document.getElementById('sidebarClose');

        if (!hamburger) return;

        const toggle = () => {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('open');
            hamburger.classList.toggle('active');
        };

        hamburger.addEventListener('click', toggle);
        if (overlay) overlay.addEventListener('click', toggle);
        if (closeBtn) closeBtn.addEventListener('click', toggle);
    },

    initMobileMenu() {
        const sidebarToggle = document.getElementById('sidebarToggle');
        const appLayout = document.querySelector('.app-layout');
        
        if (sidebarToggle && appLayout) {
            sidebarToggle.addEventListener('click', () => {
                appLayout.classList.toggle('sidebar-collapsed');
            });
        }
    },

    initParticles() {
        // Subtle background particles can be added here if needed
    },

    initClock() {
        const clockEl = document.getElementById('currentClock');
        if (!clockEl) return;

        const update = () => {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        };
        setInterval(update, 60000);
        update();
    }
};

document.addEventListener('DOMContentLoaded', () => MainApp.init());
