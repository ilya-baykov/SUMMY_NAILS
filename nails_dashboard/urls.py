from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("api/profile/", views.profile_api, name="profile_api"),
    path("api/education/", views.education_create_api, name="education_create_api"),
    path("api/education/<int:record_id>/", views.education_delete_api, name="education_delete_api"),
    path("api/portfolio/", views.portfolio_create_api, name="portfolio_create_api"),
    path("api/portfolio/<int:work_id>/", views.portfolio_delete_api, name="portfolio_delete_api"),
]
