from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('boericke/', views.remedy_compare, name='remedy_compare'),
    path('allen/', views.allen_compare, name='allen_compare'),
    path('about/', views.about, name='about'),
    path('suggestion/', views.suggestion, name='suggestion'),
    path('thanks/', views.thanks, name='thanks'),
    path('privacy/', views.privacy, name='privacy'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('api/track-search/', views.track_search_api, name='track_search_api'),
]
