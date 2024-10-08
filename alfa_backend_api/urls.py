
from django.contrib import admin
from django.urls import path,include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="ALFA-ACADEMY_ONE REST API",
      default_version='v1',
      description="This is the api used for implementing backend in ONE Web App",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="abengaristide@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('affiliates/',include('affiliates.urls')),
    path('auth/',include('authentication.urls')),
    path('notifications/',include('Notifications.urls')),
    path('publications/',include('Publications.urls')),
    path('auth/',include('djoser.urls.jwt')),
    path('payment/',include('Payment.urls')),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
