from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/', include('app.urls')),
    path('', RedirectView.as_view(url='app/')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/logged_out/', TemplateView.as_view(template_name='registration/logged_out.html'), name='logged_out'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)