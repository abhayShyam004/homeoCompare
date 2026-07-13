import os

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates"
landing_path = os.path.join(base_dir, "landing.html")

with open(landing_path, "r") as f:
    landing = f.read()

# Get head and nav
header_part = landing.split('</nav>')[0] + '</nav>\n'

# Get footer
footer = '    <!-- MAIN LANDING FOOTER -->' + landing.split('<!-- MAIN LANDING FOOTER -->')[1]

about_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827; font-family: 'Outfit', sans-serif;">About HomeoCompare</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">A precision tool built to make comparative Materia Medica research faster, cleaner, and more intuitive.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #EAE8E3; margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #131313; font-family: 'Outfit', sans-serif;">Our Mission</h2>
            <p style="color: #6B6965; line-height: 1.7; margin-bottom: 1.5rem;">HomeoCompare was designed for practitioners and students who need instant access to verified symptom differentiations without flipping through multiple heavy volumes.</p>
            <p style="color: #6B6965; line-height: 1.7;">By mapping Boericke's Materia Medica alongside Allen's Keynotes, we highlight the distinguishing characteristics, thermal modalities, and clinical affinities of each remedy in a unified interface.</p>
        </div>
    </main>
"""

privacy_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827; font-family: 'Outfit', sans-serif;">Privacy Policy</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">Your data privacy and security are our highest priority.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #EAE8E3; margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #131313; font-family: 'Outfit', sans-serif;">Data Collection</h2>
            <p style="color: #6B6965; line-height: 1.7; margin-bottom: 1.5rem;">We collect minimal data required to run the service. Any saved remedies or clinical notes are stored securely and associated only with your authenticated session.</p>
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; margin-top: 2rem; color: #131313; font-family: 'Outfit', sans-serif;">Third-Party Services</h2>
            <p style="color: #6B6965; line-height: 1.7;">We do not share or sell your personal information. Analytic services are used strictly to improve the application's performance and user experience.</p>
        </div>
    </main>
"""

feedback_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827; font-family: 'Outfit', sans-serif;">Feedback & Suggestions</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">Help us improve HomeoCompare. Found a missing rubric? Have a feature request? Let us know.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 8px 30px rgba(0,0,0,0.04); border: 1px solid #EAE8E3; margin-bottom: 2rem;">
            <form action="{% url 'submit_feedback' %}" method="POST" style="display: flex; flex-direction: column; gap: 1.5rem;">
                {% csrf_token %}
                <input type="hidden" name="_next" value="{% url 'thanks' %}">
                <input type="hidden" name="_subject" value="New Suggestion from HomeoCompare users">
                
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: #374151;">Email Address</label>
                    <input type="email" name="email" required placeholder="name@example.com" style="width: 100%; padding: 0.8rem; border: 1px solid #EAE8E3; border-radius: 10px; font-family: inherit; outline: none;">
                </div>
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: #374151;">Your Message</label>
                    <textarea name="message" rows="5" required placeholder="Tell us what you think..." style="width: 100%; padding: 0.8rem; border: 1px solid #EAE8E3; border-radius: 10px; font-family: inherit; resize: vertical; outline: none;"></textarea>
                </div>
                <button type="submit" style="background: #111827; color: white; border: none; padding: 1rem; border-radius: 9999px; font-weight: 600; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 14px rgba(0,0,0,0.2)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none'">Submit Feedback</button>
            </form>
        </div>
    </main>
"""

def write_file(filename, content):
    with open(os.path.join(base_dir, "app", filename), "w") as f:
        f.write(header_part + content + footer)

write_file("about.html", about_content)
write_file("privacy.html", privacy_content)
write_file("suggestions.html", feedback_content)

print("Pages updated successfully with correct split.")
