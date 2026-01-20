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
