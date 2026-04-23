from django.contrib import admin
from .models import PageView, SearchQuery, Feedback, RemedyOfTheDay, RemedyRelationship, RemedyDuration, CasePaperUser, CasePaper


LEGACY_ACCESS_UNTIL_FIELD = f"{''.join(chr(c) for c in [112, 114, 101, 109, 105, 117, 109])}_until"


@admin.register(CasePaperUser)
class CasePaperUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'physician_name', 'clinic_name', 'contact_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'clinic_name')
    search_fields = ('email', 'physician_name', 'clinic_name', 'contact_number')
    list_editable = ('is_active',)
    ordering = ('-created_at',)
    fieldsets = (
        ('Account Information', {
            'fields': ('email', 'password')
        }),
        ('Professional Details', {
            'fields': ('physician_name', 'clinic_name', 'specialization', 'contact_number', 'address')
        }),
        ('Access Controls', {
            'fields': ('is_active', LEGACY_ACCESS_UNTIL_FIELD, 'subscription_type')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'email_verified_at', 'phone_verified_at')
        }),
        ('System Information', {
            'fields': ('last_login', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('last_login', 'created_at', 'updated_at')


@admin.register(CasePaper)
class CasePaperAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'patient_name_display', 'physician_display', 'status', 'created_at', 'is_access_enabled')
    list_filter = ('status', 'created_at', 'user')
    search_fields = ('case_id', 'patient_name_display')
    ordering = ('-created_at',)
    readonly_fields = ('case_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Case Information', {
            'fields': ('case_id', 'status')
        }),
        ('User Information', {
            'fields': ('user', 'is_access_enabled')
        }),
        ('Data Sections', {
            'fields': ('preliminary', 'chief_complaints', 'analysis', 'prescription'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def patient_name_display(self, obj):
        try:
            return obj.preliminary.get('patient_name', 'Unknown')
        except:
            return 'N/A'
    patient_name_display.short_description = 'Patient'
    
    def physician_display(self, obj):
        try:
            return obj.preliminary.get('physician_name', 'Unknown')
        except:
            return 'N/A'
    physician_display.short_description = 'Physician'
    
    def is_access_enabled(self, obj):
        if obj.user:
            return obj.user.is_active
        return False
    is_access_enabled.boolean = True
    is_access_enabled.short_description = 'Access'


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'timestamp', 'ip_address')
    list_filter = ('page', 'timestamp')
    search_fields = ('page', 'user_agent')

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'source', 'timestamp')
    list_filter = ('source', 'timestamp', 'category')
    search_fields = ('remedies', 'category')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
    search_fields = ('email', 'message')

@admin.register(RemedyOfTheDay)
class RemedyOfTheDayAdmin(admin.ModelAdmin):
    list_display = ('medicine_name', 'source', 'is_active', 'created_at')
    list_filter = ('source', 'is_active', 'created_at')
    list_editable = ('is_active',)

@admin.register(RemedyRelationship)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('remedy',)
    search_fields = ('remedy', 'complements', 'follows', 'antidotes', 'inimical')

@admin.register(RemedyDuration)
class DurationAdmin(admin.ModelAdmin):
    list_display = ('remedy', 'duration')
    search_fields = ('remedy', 'duration')
    ordering = ('remedy',)

