/**
 * Bookmarks and Notes Manager
 * Handles local storage operations for saving remedies and notes.
 */

const BookmarksManager = {
    STORAGE_KEY: 'homeo_bookmarks',

    // Load all data from local storage
    getAll: function() {
        const data = localStorage.getItem(this.STORAGE_KEY);
        return data ? JSON.parse(data) : {};
    },

    // Save data to local storage
    saveAll: function(data) {
        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
        this.updateUI();
    },

    // Toggle bookmark status for a remedy
    toggle: function(remedyName, source, displayName) {
        const data = this.getAll();
        const key = this.generateKey(source, remedyName);

        if (data[key]) {
            delete data[key];
            this.showToast(`Removed ${displayName} from bookmarks`);
        } else {
            data[key] = {
                id: key,
                name: remedyName,
                source: source,
                displayName: displayName,
                note: '',
                timestamp: new Date().toISOString()
            };
            this.showToast(`Saved ${displayName} to bookmarks`);
        }

        this.saveAll(data);
        return !!data[key];
    },

    // Check if a remedy is bookmarked
    isBookmarked: function(remedyName, source) {
        const data = this.getAll();
        const key = this.generateKey(source, remedyName);
        return !!data[key];
    },

    // Save a note for a remedy
    saveNote: function(remedyName, source, note) {
        const data = this.getAll();
        const key = this.generateKey(source, remedyName);

        if (data[key]) {
            data[key].note = note;
            data[key].timestamp = new Date().toISOString(); // Update timestamp
            this.saveAll(data);
            this.showToast('Note saved');
        }
    },

    // Generate a unique key
    generateKey: function(source, name) {
        return `${source}_${name}`.toLowerCase().replace(/[^a-z0-9_]/g, '_');
    },

    // Update UI elements (stars) based on current state
    updateUI: function() {
        // Find all bookmark buttons
        document.querySelectorAll('.bookmark-btn').forEach(btn => {
            const name = btn.dataset.name;
            const source = btn.dataset.source;
            const isSaved = this.isBookmarked(name, source);

            if (isSaved) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fa-solid fa-star"></i>';
                btn.title = "Remove from Saved";
            } else {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="fa-regular fa-star"></i>';
                btn.title = "Save to Bookmarks";
            }
        });
        
        // Update any count badges if they exist
        const count = Object.keys(this.getAll()).length;
        document.querySelectorAll('.saved-count-badge').forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-flex' : 'none';
        });
    },
    
    // Simple toast notification
    showToast: function(message) {
        let toast = document.getElementById('bookmark-toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.id = 'bookmark-toast';
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: var(--bg-card, #1e293b);
                color: var(--text-primary, #f1f5f9);
                padding: 12px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 1px solid var(--border, #334155);
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 8px;
            `;
            // Add icon
            toast.innerHTML = '<i class="fa-solid fa-info-circle" style="color: var(--primary, #059669)"></i> <span class="msg"></span>';
            document.body.appendChild(toast);
        }
        
        toast.querySelector('.msg').textContent = message;
        toast.style.opacity = '1';
        
        if (this.toastTimeout) clearTimeout(this.toastTimeout);
        this.toastTimeout = setTimeout(() => {
            toast.style.opacity = '0';
        }, 3000);
    },

    init: function() {
        this.updateUI();
        // Bind event listeners using delegation for dynamically adding elements
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.bookmark-btn');
            if (btn) {
                e.preventDefault();
                e.stopPropagation();
                const name = btn.dataset.name;
                const source = btn.dataset.source;
                const displayName = btn.dataset.display || name;
                this.toggle(name, source, displayName);
            }
        });
    }
};

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    BookmarksManager.init();
});
