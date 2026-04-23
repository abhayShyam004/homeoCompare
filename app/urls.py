from django.urls import path
from . import views
from . import case_paper_views
from . import auth_views
from . import test_views

urlpatterns = [
    path('', views.home, name='home'),
    path('boericke/', views.remedy_compare, name='boericke_comparison'),
    path('allen/', views.allen_compare, name='allen_comparison'),
    path('about/', views.about, name='about'),
    path('saved/', views.saved_remedies, name='saved_remedies'),
    path('relationships/', views.relationships_view, name='relationships'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('thanks/', views.thanks, name='thanks'),
    path('privacy/', views.privacy, name='privacy'),
    path('history/', views.remedy_history, name='remedy_history'),
    path('durations/', views.durations_view, name='durations'),

    # Case Paper Routes
    path('clinic', case_paper_views.case_paper_dashboard),
    path('clinic/', case_paper_views.case_paper_dashboard, name='clinic_dashboard'),
    path('case_paper/', case_paper_views.case_paper_dashboard, name='case_paper_dashboard'),
    path('case_paper/new/', case_paper_views.case_paper_new, name='case_paper_new'),
    path('case_paper/cases/', case_paper_views.case_paper_cases, name='case_paper_cases'),
    path('case_paper/patients/', case_paper_views.case_paper_patients, {'section': 'registration'}, name='case_paper_patients'),
    path('case_paper/patients/registration/', case_paper_views.case_paper_patients, {'section': 'registration'}, name='case_paper_patients_registration'),
    path('case_paper/patients/queue/', case_paper_views.case_paper_patients, {'section': 'queue'}, name='case_paper_patients_queue'),
    path('case_paper/patients/directory/', case_paper_views.case_paper_patients, {'section': 'directory'}, name='case_paper_patients_directory'),
    path('case_paper/patients/billing/', case_paper_views.case_paper_patients, {'section': 'billing'}, name='case_paper_patients_billing'),
    path('case_paper/doctor-desk/', case_paper_views.case_paper_doctor_desk, {'section': 'documentation'}, name='case_paper_doctor_desk'),
    path('case_paper/doctor-desk/templates/', case_paper_views.case_paper_doctor_desk, {'section': 'documentation'}, name='case_paper_doctor_desk_templates'),
    path('case_paper/doctor-desk/virtual-opd/', case_paper_views.case_paper_doctor_desk, {'section': 'virtual'}, name='case_paper_doctor_desk_virtual'),
    path('case_paper/doctor-desk/eprescriptions/', case_paper_views.case_paper_doctor_desk, {'section': 'eprescription'}, name='case_paper_doctor_desk_eprescriptions'),
    path('case_paper/doctor-desk/lab/', case_paper_views.case_paper_doctor_desk, {'section': 'lab'}, name='case_paper_doctor_desk_lab'),
    path('case_paper/doctor-desk/requests/', case_paper_views.case_paper_doctor_desk, {'section': 'requests'}, name='case_paper_doctor_desk_requests'),
    path('case_paper/calendar/', case_paper_views.case_paper_calendar, name='case_paper_calendar'),
    path('case_paper/settings/', case_paper_views.case_paper_settings, {'section': 'profile'}, name='case_paper_settings'),
    path('case_paper/settings/profile/', case_paper_views.case_paper_settings, {'section': 'profile'}, name='case_paper_settings_profile'),
    path('case_paper/settings/workspace/', case_paper_views.case_paper_settings, {'section': 'workspace'}, name='case_paper_settings_workspace'),
    path('case_paper/settings/account/', case_paper_views.case_paper_settings, {'section': 'account'}, name='case_paper_settings_account'),
    path('clinic/<slug:public_slug>/', case_paper_views.public_clinic_page, name='public_clinic_profile'),
    path('case_paper/<str:case_id>/', case_paper_views.case_paper_view, name='case_paper_view'),
    path('case_paper/<str:case_id>/edit/', case_paper_views.case_paper_form, name='case_paper_edit'),
    path('api/case_paper/save/', case_paper_views.case_paper_save, name='case_paper_save'),
    path('api/case_paper/full_save/', case_paper_views.case_paper_full_save, name='case_paper_full_save'),
    path('api/case_paper/delete/', case_paper_views.case_paper_delete, name='case_paper_delete'),
    path('api/case_paper/get/<str:case_id>/', case_paper_views.case_paper_get_data, name='case_paper_get_data'),
    path('api/remedy/search/', case_paper_views.remedy_search, name='remedy_search'),
    path('case_paper/<str:case_id>/pdf/', case_paper_views.case_paper_pdf, name='case_paper_pdf'),

    # Authentication Routes
    path('auth/login/', auth_views.login, name='login'),
    path('auth/verify-code/', auth_views.verify_code, name='verify_code'),
    path('auth/signup/', auth_views.signup, name='signup'),
    path('auth/google-login/', auth_views.google_login, name='google_login'),
    path('auth/google/callback/', auth_views.google_callback, name='google_callback'),
    path('auth/register/', auth_views.register, name='register'),
    path('auth/logout/', auth_views.logout, name='logout'),
    
    # Diagnostic endpoints
    path('debug/email-config/', test_views.test_email_config, name='test_email_config'),

    # Custom Admin Panel Routes
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/boericke/', views.admin_boericke_list, name='admin_boericke_list'),
    path('admin-panel/boericke/', views.admin_boericke_list, name='admin_boericke'),  # Backward-compatible alias
    path('admin-panel/allen/', views.admin_allen_list, name='admin_allen_list'),
    path('admin-panel/allen/', views.admin_allen_list, name='admin_allen'),  # Backward-compatible alias
    path('admin-panel/medicine/<str:source>/<str:name>/', views.admin_medicine_detail, name='admin_medicine_detail'),
    path('admin-panel/medicine/save/', views.admin_medicine_save, name='admin_medicine_save'),
    path('admin-panel/feedback/', views.admin_feedback_list, name='admin_feedback_list'),
    path('admin-panel/feedback/', views.admin_feedback_list, name='admin_feedback'),  # Backward-compatible alias
    path('admin-panel/remedy-day/', views.admin_remedy_day, name='admin_remedy_day'),
    path('admin-panel/relationships/', views.admin_relationships_list, name='admin_relationships_list'),
    path('admin-panel/relationships/', views.admin_relationships_list, name='admin_relationships'),  # Backward-compatible alias
    path('admin-panel/relationship/save/', views.admin_relationship_save, name='admin_relationship_save'),
    path('admin-panel/durations/', views.admin_durations_list, name='admin_durations_list'),
    path('admin-panel/durations/', views.admin_durations_list, name='admin_durations'),  # Backward-compatible alias
    path('admin-panel/duration/save/', views.admin_duration_save, name='admin_duration_save'),
    path('admin-panel/users-control/', views.admin_users_control, name='admin_users_control'),
    path('admin-panel/toggle-user-access/<int:user_id>/', views.admin_toggle_user_access, name='admin_toggle_user_access'),
    path('favicon.ico', views.favicon, name='favicon'),
]
