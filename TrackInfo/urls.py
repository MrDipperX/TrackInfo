from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.defaults import page_not_found
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

from . import settings

urlpatterns = i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path('rosetta/', include('rosetta.urls')),
    path('', include('track_manage.urls'))
)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = page_not_found
