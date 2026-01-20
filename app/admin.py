from django.contrib import admin
from .models import PageView, SearchQuery, Feedback, RemedyOfTheDay, RemedyRelationship, RemedyDuration

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

