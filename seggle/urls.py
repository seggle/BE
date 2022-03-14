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
    path('api/', include('django.contrib.auth.urls')),
    path('api/', include('password.urls.general')),
    path('api/admin/', admin.site.urls),
    path('api/admin/users/', include('account.urls.admin')),
    path('api/admin/faqs/', include('faq.urls.admin')),
    path('api/users/', include('account.urls.general')),
    path('api/admin/announcements/', include('announcement.urls.admin')),
    path('api/announcements/', include('announcement.urls.general')),
    path('api/admin/class/', include('classes.urls.admin')),
    path('api/class/', include('classes.urls.general')),
    path('api/faqs/', include('faq.urls.general')),
    path('api/proposals/', include('proposal.urls')),
    path('api/problems/', include('problem.urls.general')),
    path('api/competitions/', include('competition.urls')),
    path('api/submissions/', include('submission.urls')),
    path('api/leaderboards/', include('leaderboard.urls')),
    path('api/api-auth/', include('rest_framework.urls')),
    path('api/class/<int:class_id>/contests/<int:contest_id>/exam/',include('exam.urls')),
    path('api/admin/problems/',include('problem.urls.admin')),
]