/**
 * HomeoCompare Main JS - Premium Features & Shared Logic
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
const theme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', theme);
            this.updateThemeBtn(theme);
        };

        themeToggle.addEventListener('click', () => {
            const next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            this.updateThemeBtn(next);
        });

        init();
    },

    updateThemeBtn(theme) {
        const btn = document.getElementById('themeToggle');
        if (!btn) return;
        
        const isLanding = btn.classList.contains('landing-toggle'); // Special case for current landing
        if (isLanding) {
            btn.innerHTML = `
                <span class="toggle-text">${theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                <i class="fas fa-${theme === 'dark' ? 'sun' : 'moon'}"></i>
            `;
        } else {
             // Dashboard style toggle
             const icon = theme === 'dark' ? 'sun' : 'moon';
             const text = theme === 'dark' ? 'Light Mode' : 'Dark Mode';
             btn.innerHTML = `<span><i class="fas fa-${icon}"></i> ${text}</span><i class="fas fa-chevron-right"></i>`;
        }
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
