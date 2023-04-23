from django.urls import path

from . import views

app_name = "jobs"
urlpatterns = [
    path("jobs/", views.index, name="job-index"),
    path("jobs/<str:job_id>/", views.detail, name="job-detail"),
    path("jobs/<str:job_id>/status/", views.status, name="job-status"),
]
