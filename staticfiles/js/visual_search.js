/**
 * Visual Search / Interactive Body Map
 * Handles the SVG body map modal and interactions.
 */

const BodyMapManager = {
    // Mapping SVG IDs to form values
    MAPPING: {
        'head': ['head', 'vision', 'eyes', 'ears', 'hearing', 'nose', 'face', 'mouth', 'teeth'],
        'neck': ['neck', 'throat'],
        'chest': ['respiratory', 'respiratory system', 'heart', 'cardio-vascular system'],
        'abdomen': ['stomach', 'abdomen', 'gastro-intestinal system', 'liver'],
        'pelvis': ['urinary', 'urinary system', 'male', 'female', 'male reproductive system', 'female reproductive system', 'stool', 'rectum'],
        'back': ['back'],
        'arms': ['upper limbs', 'extremities'],
        'legs': ['lower limbs', 'extremities', 'locomotor'],
        'skin': ['skin', 'perspiration', 'fever', 'modalities']
    },

    init: function() {
        this.injectModal();
        this.attachListeners();
    },

    injectModal: function() {
        if (document.getElementById('bodyMapModal')) return;

        const modalHtml = `
            <div id="bodyMapModal" class="visual-modal">
                <div class="visual-modal-content">
                    <div class="visual-header">
                        <h3><i class="fas fa-microscope"></i> Visual Symptom Localizer</h3>
                        <span class="close-visual">&times;</span>
                    </div>
                    <div class="visual-body">
                        <div class="hologram-container">
                            <div class="scan-line"></div>
                            ${this.getSVG()}
                        </div>
                        <div class="info-panel">
                            <span class="info-label">TARGET REGION</span>
                            <div id="hover-label" class="hover-text">SYSTEM STANDBY</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);

        // Add Premium Medical CSS
        const style = document.createElement('style');
        style.textContent = `
            :root {
                --holo-cyan: #00f3ff;
                --holo-blue: #0051ff;
                --holo-bg: rgba(10, 20, 30, 0.95);
            }

            .visual-modal {
                display: none; 
                position: fixed; 
                z-index: 2000; 
                left: 0; top: 0; 
                width: 100%; height: 100%; 
                background-color: rgba(0, 0, 0, 0.85); 
                align-items: center; justify-content: center;
                backdrop-filter: blur(8px);
            }
            .visual-modal-content {
                background: linear-gradient(145deg, rgba(20,20,30,0.95), rgba(10,10,20,0.98));
                border: 1px solid rgba(0, 243, 255, 0.3);
                border-radius: 12px;
                width: 95%; max-width: 500px;
                box-shadow: 0 0 30px rgba(0, 243, 255, 0.1), inset 0 0 20px rgba(0, 50, 100, 0.2);
                animation: powerOn 0.4s ease-out;
                position: relative;
                overflow: hidden;
            }
            
            /* Visual Header */
            .visual-header {
                padding: 1rem 1.5rem;
                display: flex; justify-content: space-between; align-items: center;
                border-bottom: 1px solid rgba(0, 243, 255, 0.2);
                background: rgba(0, 20, 40, 0.5);
            }
            .visual-header h3 { 
                color: var(--holo-cyan); 
                font-family: 'Courier New', monospace; 
                text-transform: uppercase; 
                letter-spacing: 1px; 
                font-size: 1rem;
                text-shadow: 0 0 5px var(--holo-cyan);
            }
            .close-visual { color: var(--text-muted); font-size: 1.5rem; cursor: pointer; transition: color 0.2s; }
            .close-visual:hover { color: var(--holo-cyan); text-shadow: 0 0 8px var(--holo-cyan); }
            
            /* Body Area */
            .visual-body { padding: 0.5rem; text-align: center; position: relative; }
            
            .hologram-container {
                height: 500px;
                position: relative;
                display: flex; justify-content: center; align-items: center;
                background: radial-gradient(circle at center, rgba(0, 50, 100, 0.1) 0%, transparent 70%);
            }
            
            /* SVG Styling */
            .medical-svg {
                height: 90%;
                filter: drop-shadow(0 0 2px rgba(0, 243, 255, 0.3));
            }
            
            .body-part { 
                fill: rgba(0, 30, 50, 0.3); 
                stroke: rgba(0, 243, 255, 0.4); 
                stroke-width: 1.5; 
                transition: all 0.3s ease; 
                cursor: pointer; 
                vector-effect: non-scaling-stroke;
            }
            
            .body-part:hover { 
                fill: rgba(0, 243, 255, 0.15); 
                stroke: var(--holo-cyan); 
                stroke-width: 2.5; 
                filter: drop-shadow(0 0 8px var(--holo-cyan));
            }

            /* Info Panel at Bottom */
            .info-panel {
                position: absolute;
                bottom: 20px; left: 50%; transform: translateX(-50%);
                background: rgba(0, 10, 20, 0.8);
                border: 1px solid var(--holo-cyan);
                padding: 10px 20px;
                border-radius: 4px;
                min-width: 200px;
                box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            }
            .info-label {
                display: block;
                font-size: 0.6rem;
                color: #5588aa;
                letter-spacing: 2px;
                margin-bottom: 4px;
            }
            .hover-text {
                color: white;
                font-family: 'Courier New', monospace;
                font-weight: 700;
                font-size: 1.2rem;
                text-shadow: 0 0 5px white;
                text-transform: uppercase;
            }

            /* Scan Line Animation */
            .scan-line {
                position: absolute;
                top: 0; left: 0; width: 100%; height: 2px;
                background: rgba(0, 243, 255, 0.5);
                box-shadow: 0 0 10px var(--holo-cyan);
                animation: scan 3s linear infinite;
                pointer-events: none;
                z-index: 10;
                opacity: 0.5;
            }

            @keyframes scan {
                0% { top: 0%; opacity: 0; }
                10% { opacity: 1; }
                90% { opacity: 1; }
                100% { top: 100%; opacity: 0; }
            }
            @keyframes powerOn {
                0% { transform: scale(0.95); opacity: 0; filter: brightness(0.5); }
                50% { filter: brightness(1.5); }
                100% { transform: scale(1); opacity: 1; filter: brightness(1); }
            }
        `;
        document.head.appendChild(style);
    },

    getSVG: function() {
        // High-fidelity Human Anatomy Silhouette
        return `
            <svg class="medical-svg" viewBox="0 0 400 800" xmlns="http://www.w3.org/2000/svg">
                <defs>
                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur"/>
                        <feMerge>
                            <feMergeNode in="coloredBlur"/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>
                
                <!-- HEAD & NECK -->
                <path id="part-head" class="body-part" d="M200,40 C175,40 160,60 160,95 C160,125 175,145 200,145 C225,145 240,125 240,95 C240,60 225,40 200,40 Z" />
                <path id="part-neck" class="body-part" d="M185,145 L180,175 L220,175 L215,145 Z" />

                <!-- CHEST / THORAX (Lungs/Heart) -->
                <path id="part-chest" class="body-part" d="M160,175 L240,175 L260,200 L250,300 L150,300 L140,200 L160,175 Z" />

                <!-- ABDOMEN (Stomach/Liver) -->
                <path id="part-abdomen" class="body-part" d="M150,300 L250,300 L245,380 L155,380 Z" />

                <!-- PELVIS (Urinary/Repro) -->
                <path id="part-pelvis" class="body-part" d="M155,380 L245,380 L235,440 L200,460 L165,440 Z" />

                <!-- ARMS -->
                <!-- Right Arm (viewer's left) -->
                <path id="part-arms-left" class="body-part part-arms" d="M140,200 L110,210 L90,320 L70,330 L80,350 L110,340 L130,220" />
                <!-- Left Arm (viewer's right) -->
                <path id="part-arms-right" class="body-part part-arms" d="M260,200 L290,210 L310,320 L330,330 L320,350 L290,340 L270,220" />

                <!-- LEGS -->
                <!-- Right Leg -->
                <path id="part-legs-left" class="body-part part-legs" d="M165,440 L200,460 L195,550 L185,730 L160,730 L155,550 L155,440" />
                <!-- Left Leg -->
                <path id="part-legs-right" class="body-part part-legs" d="M235,440 L200,460 L205,550 L215,730 L240,730 L245,550 L245,440" />
            </svg>
        `;
    },

    attachListeners: function() {
        const modal = document.getElementById('bodyMapModal');
        const closeBtn = modal.querySelector('.close-visual');
        const label = document.getElementById('hover-label');

        // Open Modal
        document.querySelectorAll('.open-visual-search').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                modal.style.display = 'flex';
            });
        });

        // Close Modal
        closeBtn.onclick = () => modal.style.display = 'none';
        window.onclick = (e) => {
            if (e.target == modal) modal.style.display = 'none';
        };

        // Interactive parts (handle merged parts like arms/legs)
        const parts = document.querySelectorAll('.body-part');
        parts.forEach(part => {
            let id = part.id.replace('part-', '');
            if (id.includes('arms')) id = 'arms';
            if (id.includes('legs')) id = 'legs';
            
            // Hover
            part.addEventListener('mouseenter', () => {
                label.textContent = id.toUpperCase();
                // Highlight duplicates (e.g. both arms)
                document.querySelectorAll(`.part-${id}`).forEach(p => p.style.fill = 'rgba(0, 243, 255, 0.3)');
            });
            
            part.addEventListener('mouseleave', () => {
                label.textContent = 'SYSTEM STANDBY';
                document.querySelectorAll(`.part-${id}`).forEach(p => p.style.fill = '');
            });

            // Click
            part.addEventListener('click', () => {
                this.handleSelection(id);
                modal.style.display = 'none';
            });
        });
    },

    handleSelection: function(partId) {
        const potentialValues = this.MAPPING[partId];
        const select = document.getElementById('symptom');
        
        if (!select || !potentialValues) return;

        // Try to find the best matching option in the dropdown
        let bestMatch = '';
        for (const option of select.options) {
            const val = option.value.toLowerCase();
            // Exact match
            if (potentialValues.includes(val)) {
                bestMatch = val;
                break;
            }
            // Partial match (if no exact found yet)
            if (!bestMatch && potentialValues.some(pv => val.includes(pv))) {
                bestMatch = val;
            }
        }

        if (bestMatch) {
            select.value = bestMatch;
            // Trigger change event to update chips/UI
            select.dispatchEvent(new Event('change'));
            
            // Toast
            if (window.BookmarksManager) {
                BookmarksManager.showToast(`Selected category: ${bestMatch}`);
            }
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    BodyMapManager.init();
});
