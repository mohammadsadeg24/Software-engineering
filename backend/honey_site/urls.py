from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
# from honey_api.admin import mongo_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin/', mongo_admin.urls),
    path('user/', include('core.urls')),
    path('honey_api/', include('honey_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
