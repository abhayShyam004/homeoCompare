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
