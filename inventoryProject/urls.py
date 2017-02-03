"""inventoryProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

urlpatterns = [
<<<<<<< HEAD
    url(r'^admin/', admin.site.urls),
    url(r'^api/request/', include('inventory_requests.urls')),
    url(r'^accounts/logout/$', auth_views.logout),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^accounts/$', RedirectView.as_view(url='/')),
    url(r'^item/', include('items.urls')),
    url(r'^log/', include('inventory_logger.urls')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
=======
    url(r'^api/admin/', admin.site.urls),
    url(r'^api/', include('inventory_requests.urls')),
    url(r'^api/accounts/logout/$', auth_views.logout),
    url(r'^api/accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}),
    url(r'^api/accounts/$', RedirectView.as_view(url='/')),
    url(r'^api/item/', include('items.urls')),
    url(r'^api/user/', include('inventory_user.urls')),
    url(r'^api/log/', include('inventory_logger.urls')),
    url(r'^api/o/', include('oauth2_provider.urls', namespace='oauth2_provider'))
>>>>>>> cf4a7366b66ad60ee28be0ce4e8b909ee513a1c9
]
