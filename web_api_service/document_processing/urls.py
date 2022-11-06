"""document_processing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from account import views as user_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from document_processing import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Обработка документов API",
      default_version='v1',
      description="Взаимодействия с API (поиск, скачивание отчетов и т.д.)",
      terms_of_service="http://documents.dueva-hack.ru",
      contact=openapi.Contact(email="labdevs@yandex.ru"),
      license=openapi.License(name="Test License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),

    path('register/', user_views.register, name='register_url'),
    path('login/', auth_views.LoginView.as_view(template_name='account/login.html'), name='login_url'),
    path('logout/', auth_views.LogoutView.as_view(template_name='account/logout.html'), name='logout_url'),
    path('', user_views.main_page, name='main_page_url'),
    path('account/', include('account.urls')),
    path('document/', include('document.urls')),

    # REST FRAMEWORK URLS
    path('api/v1/', include('document.api.urls', 'document_api')),
    path('api/v1/account/', include('account.api.urls', 'account_api')),
    # url('swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
