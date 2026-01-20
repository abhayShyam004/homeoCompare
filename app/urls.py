from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('boericke/', views.remedy_compare, name='remedy_compare'),
    path('allen/', views.allen_compare, name='allen_compare'),
    path('about/', views.about, name='about'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('thanks/', views.thanks, name='thanks'),
    path('saved-remedies/', views.saved_remedies, name='saved_remedies'),
    path('relationships/', views.relationships_view, name='relationships'),
    path('privacy/', views.privacy, name='privacy'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/boericke/', views.admin_boericke_list, name='admin_boericke'),
    path('admin-panel/allen/', views.admin_allen_list, name='admin_allen'),
    path('admin-panel/medicine/<str:source>/<str:name>/', views.admin_medicine_detail, name='admin_medicine_detail'),
    path('admin-panel/medicine/save/', views.admin_medicine_save, name='admin_medicine_save'),
    
    # Relationships
    path('admin-panel/relationships/', views.admin_relationships_list, name='admin_relationships'),
    path('admin-panel/relationships/save/', views.admin_relationship_save, name='admin_relationship_save'),

    # Durations
    path('durations/', views.durations_view, name='durations'),
    path('admin-panel/durations/', views.admin_durations_list, name='admin_durations'),
    path('admin-panel/durations/save/', views.admin_duration_save, name='admin_duration_save'),

    path('api/track-search/', views.track_search_api, name='track_search_api'),
    
    # Feedback
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('admin-panel/feedback/', views.admin_feedback_list, name='admin_feedback'),
    
    # Remedy of the Day
    path('admin-panel/remedy-of-day/', views.admin_remedy_day, name='admin_remedy_day'),
    path('remedy-history/', views.remedy_history, name='remedy_history'),
    path('remedy-history/<int:remedy_id>/', views.remedy_history, name='remedy_history_detail'),
]

