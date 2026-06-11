from django.urls import path

from . import views


app_name = "dashboard"

urlpatterns = [
    path("login/", views.login_page, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("booking/", views.booking_page, name="booking"),
    path("staff/", views.staff_panel, name="staff_panel"),
    path("api/dashboard/", views.dashboard_api, name="dashboard_api"),
    path("api/profile/", views.profile_api, name="profile_api"),
    path("api/shift/toggle/", views.shift_toggle_api, name="shift_toggle_api"),
    path("api/appointments/<int:appointment_id>/close/", views.appointment_close_api, name="appointment_close_api"),
    path("api/education/", views.education_create_api, name="education_create_api"),
    path("api/education/<int:record_id>/", views.education_delete_api, name="education_delete_api"),
    path("api/portfolio/", views.portfolio_create_api, name="portfolio_create_api"),
    path("api/portfolio/<int:work_id>/", views.portfolio_delete_api, name="portfolio_delete_api"),
    path("api/public-booking/", views.public_booking_api, name="public_booking_api"),
    path("api/manage/", views.manage_api, name="manage_api"),
    path("api/manage/services/", views.service_create_api, name="service_create_api"),
    path("api/manage/services/<int:service_id>/", views.service_delete_api, name="service_delete_api"),
    path("api/manage/appointments/", views.staff_appointment_create_api, name="staff_appointment_create_api"),
    path("api/manage/payouts/", views.payout_create_api, name="payout_create_api"),
]
