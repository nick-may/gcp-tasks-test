from django.urls import include, path
from django.conf import settings

from sample_app import views
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_cloud_tasks.urls")),
    path("create-person", views.PersonCreateView.as_view()),
    path("replace-person", views.PersonReplaceView.as_view()),
    path("test", views.TestView.as_view()),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
