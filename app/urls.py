from django.urls import path
from . import views
from . import case_paper_views
from . import auth_views

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
    
    # Case Paper (Premium Feature) - Hidden route
    path('case_paper/login/', case_paper_views.case_paper_login, name='case_paper_login'),
    path('case_paper/logout/', case_paper_views.case_paper_logout, name='case_paper_logout'),
    path('case_paper/', case_paper_views.case_paper_dashboard, name='case_paper_dashboard'),
    path('case_paper/new/', case_paper_views.case_paper_new, name='case_paper_new'),
    path('case_paper/cases/', case_paper_views.case_paper_cases, name='case_paper_cases'),
    path('case_paper/patients/', case_paper_views.case_paper_patients, name='case_paper_patients'),
    path('case_paper/calendar/', case_paper_views.case_paper_calendar, name='case_paper_calendar'),
    path('case_paper/settings/', case_paper_views.case_paper_settings, name='case_paper_settings'),
    path('case_paper/<str:case_id>/', case_paper_views.case_paper_view, name='case_paper_view'),
    path('case_paper/<str:case_id>/edit/', case_paper_views.case_paper_form, name='case_paper_edit'),
    path('api/case_paper/save/', case_paper_views.case_paper_save, name='case_paper_save'),
    path('api/case_paper/full_save/', case_paper_views.case_paper_full_save, name='case_paper_full_save'),
    path('api/case_paper/delete/', case_paper_views.case_paper_delete, name='case_paper_delete'),
    path('api/case_paper/get/<str:case_id>/', case_paper_views.case_paper_get_data, name='case_paper_get_data'),
    
    # Authentication Routes
    path('auth/login/', auth_views.login, name='login'),
    path('auth/verify-code/', auth_views.verify_code, name='verify_code'),
    path('auth/signup/', auth_views.signup, name='signup'),
    path('auth/google-login/', auth_views.google_login, name='google_login'),
    path('auth/google/callback/', auth_views.google_callback, name='google_callback'),
    path('auth/register/', auth_views.register, name='register'),
    path('auth/logout/', auth_views.logout, name='logout'),
]

