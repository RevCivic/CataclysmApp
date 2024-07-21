from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include("landing.urls")),
    path('armor/', include("armor.urls")),
    path('events/', include("events.urls")),
    path('factions/', include("factions.urls")),
    path('people/', include('people.urls')),
    path('species/', include("species.urls")),
    path('weapons/', include("weapons.urls")),
    path('worlds/', include("worlds.urls")),
    path('adminflow/', include("adminflow.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
