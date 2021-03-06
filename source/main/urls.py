from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include

from crmapp.views.order import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('', include('crmapp.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include('api.urls')),
    path("telegram-bot/", include("tgbot.urls"))  # Включить при использование бота в режиме webhook
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
