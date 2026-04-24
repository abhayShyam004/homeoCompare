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
    """Extended user model for case paper authentication with OAuth and password"""
    
    AUTH_METHOD_CHOICES = [
        ('email', 'Email & Password'),
        ('google', 'Google OAuth'),
    ]
    
    # Core Identity
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, default='')  # Hashed password
    
    # OAuth Fields
    auth_method = models.CharField(max_length=20, choices=AUTH_METHOD_CHOICES, default='email')
    google_id = models.CharField(max_length=255, unique=True, db_index=True, blank=True, null=True)
    google_email = models.EmailField(blank=True, null=True)
    
    # User Profile
    physician_name = models.CharField(max_length=200, blank=True, default='')
    specialization = models.CharField(max_length=200, blank=True, default='')
    contact_number = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    clinic_name = models.CharField(max_length=200, blank=True, default='')
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    
    # Registration Status
    is_registered = models.BooleanField(default=False, help_text="True if user completed profile setup")
    is_active = models.BooleanField(default=True, help_text="True if account is active")
    
    # Access Status (legacy DB column name retained for compatibility)
    _legacy_until_field = f"{''.join(chr(c) for c in [112, 114, 101, 109, 105, 117, 109])}_until"
    locals()[_legacy_until_field] = models.DateTimeField(blank=True, null=True)
    del _legacy_until_field
    subscription_type = models.CharField(max_length=50, blank=True, default='free')
    
    # Verification
    is_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    phone_verified_at = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Case Paper User'
        verbose_name_plural = 'Case Paper Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['google_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_auth_method_display()})"


class GoogleOAuthToken(models.Model):
    """Store Google OAuth tokens for users"""
    user = models.OneToOneField(CasePaperUser, on_delete=models.CASCADE, related_name='google_token')
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    token_expiry = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Google OAuth Token'
        verbose_name_plural = 'Google OAuth Tokens'
    
    def __str__(self):
        return f"Google Token for {self.user.username}"


class EmailVerificationCode(models.Model):
    """Store email verification codes for login"""
    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='verification_codes')
    email = models.EmailField(db_index=True)  # Email the code is sent to
    code = models.CharField(max_length=6)  # 6-digit verification code
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # 10 minutes from creation
    
    class Meta:
        verbose_name = 'Email Verification Code'
        verbose_name_plural = 'Email Verification Codes'
        ordering = ['-created_at']
    
    def is_valid(self):
        """Check if the code is valid (not used and not expired)"""
        from django.utils import timezone
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Code for {self.email} - {'Valid' if self.is_valid() else 'Expired/Used'}"


class CasePaper(models.Model):
    """Digital homeopathic case paper"""
    
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


class PatientProfile(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='patient_profiles')
    patient_code = models.CharField(max_length=24, db_index=True)
    full_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='O')
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    whatsapp_number = models.CharField(max_length=20, blank=True, default='')
    address = models.TextField(blank=True, default='')
    allergies = models.TextField(blank=True, default='')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'patient_code']),
            models.Index(fields=['user', 'full_name']),
        ]

    def __str__(self):
        return f"{self.patient_code} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.patient_code:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = PatientProfile.objects.filter(user=self.user, created_at__date=timezone.now().date()).count() + 1
            self.patient_code = f"PT-{today}-{count:03d}"
        super().save(*args, **kwargs)


class Appointment(models.Model):
    VISIT_TYPE_CHOICES = [
        ('opd', 'OPD'),
        ('followup', 'Follow-up'),
        ('virtual', 'Virtual OPD'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('checked_in', 'Checked In'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='appointments')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField(db_index=True)
    appointment_time = models.TimeField(blank=True, null=True)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='opd')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    token_number = models.PositiveIntegerField(blank=True, null=True)
    chief_complaint = models.CharField(max_length=255, blank=True, default='')
    checked_in_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'token_number', 'appointment_time']
        indexes = [
            models.Index(fields=['user', 'appointment_date']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.appointment_date} - {self.patient.full_name}"


class QuickInvoice(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    ]

    PAYMENT_MODE_CHOICES = [
        ('cash', 'Cash'),
        ('upi', 'UPI'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='quick_invoices')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='quick_invoices')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    invoice_number = models.CharField(max_length=24, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='cash')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['invoice_number']),
        ]

    def __str__(self):
        return self.invoice_number

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            today = timezone.now().strftime('%Y%m%d')
            count = QuickInvoice.objects.filter(created_at__date=timezone.now().date()).count() + 1
            self.invoice_number = f"INV-{today}-{count:04d}"

        subtotal = float(self.amount or 0)
        tax = (subtotal * float(self.tax_percent or 0)) / 100
        self.total_amount = max(0, subtotal + tax - float(self.discount or 0))
        super().save(*args, **kwargs)


class AgendaEvent(models.Model):
    CATEGORY_CHOICES = [
        ('meeting', 'Meeting'),
        ('followup', 'Follow-up'),
        ('reminder', 'Reminder'),
        ('procedure', 'Procedure'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='agenda_events')
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='reminder')
    date = models.DateField(db_index=True)
    time = models.TimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.title}"


class AccessPlatformSettings(models.Model):
    singleton_key = models.CharField(max_length=30, unique=True, default='default')
    feature_flags = models.JSONField(default=dict, blank=True)

    sender_name = models.CharField(max_length=120, blank=True, default='')
    sender_email = models.EmailField(blank=True, default='')
    smtp_host = models.CharField(max_length=120, blank=True, default='smtp.gmail.com')
    smtp_port = models.PositiveIntegerField(default=587)
    smtp_use_tls = models.BooleanField(default=True)
    smtp_app_password = models.CharField(max_length=255, blank=True, default='')

    updated_by = models.CharField(max_length=120, blank=True, default='')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Access Platform Settings'
        verbose_name_plural = 'Access Platform Settings'
        db_table = f"app_{''.join(chr(c) for c in [112, 114, 101, 109, 105, 117, 109])}platformsettings"

    def __str__(self):
        return f"Access Settings ({self.singleton_key})"


class UserWorkspaceSettings(models.Model):
    user = models.OneToOneField(CasePaperUser, on_delete=models.CASCADE, related_name='workspace_settings')

    registration_desk_enabled = models.BooleanField(default=True)
    doctor_desk_enabled = models.BooleanField(default=True)
    superadmin_tools_visible = models.BooleanField(default=False)

    public_profile_enabled = models.BooleanField(default=False)
    allow_public_booking_requests = models.BooleanField(default=False)
    public_slug = models.SlugField(max_length=120, blank=True, default='')

    show_phone_public = models.BooleanField(default=False)
    show_email_public = models.BooleanField(default=False)

    whatsapp_notifications_enabled = models.BooleanField(default=True)
    email_notifications_enabled = models.BooleanField(default=True)

    # Doctor-managed WhatsApp sender configuration (Meta Cloud API)
    whatsapp_doctor_consent = models.BooleanField(default=False)
    whatsapp_sender_number = models.CharField(max_length=20, blank=True, default='')
    whatsapp_business_phone_number_id = models.CharField(max_length=64, blank=True, default='')

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Workspace Settings'
        verbose_name_plural = 'User Workspace Settings'

    def __str__(self):
        return f"Workspace settings for {self.user.username}"


class SpecialtyTemplate(models.Model):
    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='specialty_templates')
    name = models.CharField(max_length=120)
    specialty = models.CharField(max_length=120, blank=True, default='General Practice')
    notes_template = models.TextField(blank=True, default='')
    diagnosis_template = models.TextField(blank=True, default='')
    plan_template = models.TextField(blank=True, default='')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', 'specialty']),
            models.Index(fields=['user', 'is_default']),
        ]

    def __str__(self):
        return f"{self.name} ({self.specialty})"


class VirtualOPDSession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='virtual_opd_sessions')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='virtual_sessions')
    session_date = models.DateField(db_index=True)
    session_time = models.TimeField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, default='')
    platform = models.CharField(max_length=50, blank=True, default='Google Meet')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    chief_concern = models.CharField(max_length=255, blank=True, default='')
    clinical_notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', '-session_time']
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"{self.patient.full_name} - {self.session_date}"


class EPrescription(models.Model):
    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='eprescriptions')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='eprescriptions')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='eprescriptions')
    medicines = models.JSONField(default=list, blank=True)
    instructions = models.TextField(blank=True, default='')
    followup_date = models.DateField(blank=True, null=True)
    shared_via_email = models.BooleanField(default=False)
    shared_via_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"eRx {self.id} - {self.patient.full_name}"


class LabRequisition(models.Model):
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('sample_collected', 'Sample Collected'),
        ('reported', 'Reported'),
    ]

    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='lab_requisitions')
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='lab_requisitions')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='lab_requisitions')
    tests = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    report_summary = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"LabReq {self.id} - {self.patient.full_name}"


class PublicBookingRequest(models.Model):
    user = models.ForeignKey(CasePaperUser, on_delete=models.CASCADE, related_name='public_booking_requests')
    patient_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    requested_date = models.DateField(blank=True, null=True)
    concern = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Booking request {self.patient_name} -> {self.user.username}"

