
import os
import django
import sys
from django.core.files import File

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicomp.settings')
django.setup()

from app.models import RemedyOfTheDay

def fix_image():
    # 0. Path to user image
    img_path = r"C:/Users/abhay/.gemini/antigravity/brain/f2fef114-a991-40f1-9e97-fa932c0b3e6e/uploaded_image_1768548279296.png"
    
    if not os.path.exists(img_path):
        print(f"Image not found at: {img_path}")
        return

    # 1. Clear existing active remedies
    print("Clearing active remedies...")
    RemedyOfTheDay.objects.all().delete()
    
    # 2. Create new one
    print("Creating verification remedy...")
    with open(img_path, 'rb') as f:
        remedy = RemedyOfTheDay.objects.create(
            medicine_name="VERATRUM ALBUM",
            source="allen",
            description="[MENTAL GENERALS]: Cannot bear to be left alone yet persistently refuses to talk. Thinks she is pregnant or will soon be delivered. Mania with desire to cut and tear everything, especially clothes (Tarent.) with lewd, lascivious talk, amorous or religious (Hyos., Stram.).",
            is_active=True
        )
        remedy.image.save("veratrum.png", File(f), save=True)
        
    print(f"Created: {remedy.medicine_name}")
    print(f"Image URL: {remedy.image.url}")

if __name__ == "__main__":
    fix_image()
