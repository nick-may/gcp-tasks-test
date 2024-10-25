from django.urls import include, path

from sample_app import views
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("django_cloud_tasks.urls")),
    path("create-person", views.PersonCreateView.as_view()),
    path("replace-person", views.PersonReplaceView.as_view()),
    path("test", views.TestView.as_view()),
]
