from django.db import models

# Analytics Models

class PageView(models.Model):
    """Track page views for analytics"""
    page = models.CharField(max_length=100)  # e.g., 'home', 'boericke', 'allen'
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.page} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class SearchQuery(models.Model):
    """Track remedy comparison searches"""
    remedies = models.JSONField(default=list)  # List of remedy names
    category = models.CharField(max_length=100)  # Symptom category
    source = models.CharField(max_length=20, default='boericke')  # 'boericke' or 'allen'
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Search queries'
    
    def __str__(self):
        return f"{', '.join(self.remedies)} - {self.category}"


class Feedback(models.Model):
    """Store user feedback/suggestions"""
    email = models.EmailField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Feedback'
    
    def __str__(self):
        return f"{self.email} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


class RemedyOfTheDay(models.Model):
    """Store the curated remedy of the day"""
    medicine_name = models.CharField(max_length=200)
    source = models.CharField(max_length=20, default='boericke')
    description = models.TextField(help_text="Short daily insight or keynotes about this remedy.")
    image = models.ImageField(upload_to='remedies/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Remedies of the Day'
    
    def __str__(self):
        return f"{self.medicine_name} ({self.created_at.date()})"
    
        super().save(*args, **kwargs)


class RemedyRelationship(models.Model):
    """
    Stores Dr. Gibson Miller's remedy relationships.
    Columns: Remedy, Complements, Follows Well, Antidotes, Inimical.
    """
    remedy = models.CharField(max_length=200, unique=True, help_text="Name of the primary remedy")
    complements = models.TextField(blank=True, help_text="Remedies that act as complements")
    follows = models.TextField(blank=True, help_text="Remedies that operate well after this")
    antidotes = models.TextField(blank=True, help_text="Remedies that antidote this one")
    inimical = models.TextField(blank=True, help_text="Incompatible remedies")
    
    class Meta:
        verbose_name = "Remedy Relationship"
        verbose_name_plural = "Relationship Table (Gibson Miller)"
        ordering = ['remedy']

    def __str__(self):
        return self.remedy


class RemedyDuration(models.Model):
    """
    Stores duration of action for remedies.
    """
    remedy = models.CharField(max_length=200, unique=True, help_text="Name of the remedy")
    duration = models.CharField(max_length=100, help_text="Duration of action (e.g., '30-40 days')")
    
    class Meta:
        verbose_name = "Remedy Duration"
        verbose_name_plural = "Remedy Durations"
        ordering = ['remedy']

    def __str__(self):
        return f"{self.remedy} - {self.duration}"


class CasePaperUser(models.Model):
    """User model for case paper authentication (passwordless, extensible)"""
    # Authentication
    username = models.CharField(max_length=150, unique=True, db_index=True)
    
    # Physician Profile (extensible for password auth later)
    physician_name = models.CharField(max_length=200, blank=True, default='')
    contact_number = models.CharField(max_length=20, blank=True, default='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['username']
        verbose_name = 'Case Paper User'
        verbose_name_plural = 'Case Paper Users'
    
    def __str__(self):
        return f"{self.username} - {self.physician_name}" if self.physician_name else self.username


class CasePaper(models.Model):
    """Premium feature: Digital homeopathic case paper"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('complete', 'Complete'),
    ]
    
    # User reference - who owns this case paper
    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, null=True, blank=True, related_name='case_papers')
    
    # Identity
    case_id = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    # Section 1: Preliminary Data
    preliminary = models.JSONField(default=dict, blank=True)
    # {date_time, physician_name, patient_name, age, sex, address, contact, occupation, 
    #  marital_status, religion, socioeconomic_status}
    
    # Section 2-3: Complaints
    chief_complaints = models.JSONField(default=list, blank=True)
    # [{name, duration, location, sensation, aggravation, amelioration, concomitants, intensity}]
    associated_complaints = models.JSONField(default=list, blank=True)
    
    # Section 4-6: History
    history = models.JSONField(default=dict, blank=True)
    # {hpi: {onset, duration, progress, causative_factors, sequence, previous_treatments},
    #  past_history: [...], family_history: {...}}
    
    # Section 7-9: Generals
    generals = models.JSONField(default=dict, blank=True)
    # {personal: {...}, mental_generals: {...}, physical_generals: {...}}
    
    # Section 10-11: Clinical
    clinical = models.JSONField(default=dict, blank=True)
    # {examination: {general, systemic, local}, investigations: {...}}
    
    # Section 12-16: Analysis
    analysis = models.JSONField(default=dict, blank=True)
    # {diagnosis, totality_of_symptoms, rubrics, repertorial_result, 
    #  miasmatic_analysis, remedy_differentiation, keynotes}
    
    # Section 17-18: Prescription
    prescription = models.JSONField(default=dict, blank=True)
    # {final_remedy, potency, dose, repetition, mode_of_administration, 
    #  diet_advice, restrictions, instructions}
    
    # Section 19-20: Follow-up
    followup = models.JSONField(default=list, blank=True)
    # [{date, changes, generals, new_symptoms, overall_feeling, assessment, 
    #   prescription, next_followup}]
    
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Case Paper'
        verbose_name_plural = 'Case Papers'
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['case_id']),
            models.Index(fields=['user', '-updated_at']),
        ]
    
    def __str__(self):
        patient_name = self.preliminary.get('patient_name', 'Unknown') if isinstance(self.preliminary, dict) else 'Unknown'
        return f"{self.case_id} - {patient_name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.case_id:
            # Auto-generate case ID: HC-YYYYMMDD-XXXX
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            # Count cases created today
            from django.db.models.functions import TruncDate
            today_count = CasePaper.objects.filter(
                created_at__date=timezone.now().date()
            ).count() + 1
            self.case_id = f"HC-{today}-{today_count:04d}"
        super().save(*args, **kwargs)
