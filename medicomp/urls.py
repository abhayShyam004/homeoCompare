from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from app.sitemaps import StaticSitemap  # Adjust 'app' to your app name

sitemaps = {
    'static': StaticSitemap,
}

from app.views_import_temp import trigger_import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('import-data-temp/', trigger_import, name='import_data_temp'),
    path('', include('app.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
