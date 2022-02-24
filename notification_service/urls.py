"""notification_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from notifications import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'mailings', views.MailingViewSet)
router.register(r'client', views.ClientViewSet)
router.register(r'message', views.MessageViewSet)
router.register(r'operator', views.OperatorViewSet)
router.register(r'tag', views.TagViewSet)


urlpatterns = [
    # path('admin/', admin.site.urls),  # админа не использовал и не создавал
    path('', include(router.urls)),
    # path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),  # можно подключить авторизацию

    # OpenAPI 3 documentation with Swagger UI
    path("schema/", SpectacularAPIView.as_view(), name="schema"),  # YAML
    path(
        "docs/", SpectacularSwaggerView.as_view(template_name="swagger-ui.html", url_name="schema"), name="swagger-ui",
    ),

]
