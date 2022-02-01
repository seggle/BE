"""seggle URL Configuration

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/users/', include('account.urls.admin')),
    path('admin/faqs/', include('faq.urls.admin')),
    path('users/', include('account.urls.general')),
    path('admin/announcements/', include('announcement.urls.admin')),
    path('announcements/', include('announcement.urls.general')),
    path('class/', include('classes.urls')),
    path('faqs/', include('faq.urls.general')),
    path('proposals/', include('proposal.urls')),
    path('api-auth/', include('rest_framework.urls')),
]