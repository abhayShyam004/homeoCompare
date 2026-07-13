import os

base_dir = "/run/media/abhay/Abhay/vsCODE/homeoCompare/app/templates"
landing_path = os.path.join(base_dir, "landing.html")

with open(landing_path, "r") as f:
    landing = f.read()

# Extract parts
head_nav = landing.split('<div class="dashboard-grid">')[0]
footer = '    <!-- MAIN LANDING FOOTER -->' + landing.split('<!-- MAIN LANDING FOOTER -->')[1]

# We need to close the tags that head_nav opened but dashboard-grid closed.
# Actually, dashboard-grid is the main layout, so we just use <main> instead.
# head_nav contains up to <div class="dashboard-grid">. We just need to close the things properly.

# Let's cleanly just take from <head> to end of <nav class="top-navbar">
header_part = landing.split('<!-- HERO / GREETING (For desktop it shows above columns) -->')[0]

about_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827;">About HomeoCompare</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">A precision tool built to make comparative Materia Medica research faster, cleaner, and more intuitive.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #E5E7EB; margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #1F2937;">Our Mission</h2>
            <p style="color: #4B5563; line-height: 1.7; margin-bottom: 1.5rem;">HomeoCompare was designed for practitioners and students who need instant access to verified symptom differentiations without flipping through multiple heavy volumes.</p>
            <p style="color: #4B5563; line-height: 1.7;">By mapping Boericke's Materia Medica alongside Allen's Keynotes, we highlight the distinguishing characteristics, thermal modalities, and clinical affinities of each remedy in a unified interface.</p>
        </div>
    </main>
"""

privacy_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827;">Privacy Policy</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">Your data privacy and security are our highest priority.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #E5E7EB; margin-bottom: 2rem;">
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; color: #1F2937;">Data Collection</h2>
            <p style="color: #4B5563; line-height: 1.7; margin-bottom: 1.5rem;">We collect minimal data required to run the service. Any saved remedies or clinical notes are stored securely and associated only with your authenticated session.</p>
            <h2 style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem; margin-top: 2rem; color: #1F2937;">Third-Party Services</h2>
            <p style="color: #4B5563; line-height: 1.7;">We do not share or sell your personal information. Analytic services are used strictly to improve the application's performance and user experience.</p>
        </div>
    </main>
"""

feedback_content = """
    <main style="max-width: 800px; margin: 4rem auto; flex: 1; padding: 0 1.5rem; width: 100%;">
        <h1 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 1rem; color: #111827;">Feedback & Suggestions</h1>
        <p style="font-size: 1.1rem; color: #4B5563; margin-bottom: 2rem;">Help us improve HomeoCompare. Found a missing rubric? Have a feature request? Let us know.</p>
        
        <div style="background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #E5E7EB; margin-bottom: 2rem;">
            <form action="{% url 'submit_feedback' %}" method="POST" style="display: flex; flex-direction: column; gap: 1.5rem;">
                {% csrf_token %}
                <input type="hidden" name="_next" value="{% url 'thanks' %}">
                <input type="hidden" name="_subject" value="New Suggestion from HomeoCompare users">
                
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: #374151;">Email Address</label>
                    <input type="email" name="email" required placeholder="name@example.com" style="width: 100%; padding: 0.8rem; border: 1px solid #D1D5DB; border-radius: 10px; font-family: inherit;">
                </div>
                <div>
                    <label style="display: block; font-weight: 500; margin-bottom: 0.5rem; color: #374151;">Your Message</label>
                    <textarea name="message" rows="5" required placeholder="Tell us what you think..." style="width: 100%; padding: 0.8rem; border: 1px solid #D1D5DB; border-radius: 10px; font-family: inherit; resize: vertical;"></textarea>
                </div>
                <button type="submit" style="background: #111827; color: white; border: none; padding: 1rem; border-radius: 12px; font-weight: 600; cursor: pointer; transition: background 0.2s;">Submit Feedback</button>
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

print("Pages updated successfully.")
