from django.contrib import admin

from .models import Appointment, EducationRecord, FinanceOperation, MedicalBook, PortfolioWork, Service, Shift


@admin.register(MedicalBook)
class MedicalBookAdmin(admin.ModelAdmin):
    list_display = ("number", "valid_until", "status", "updated_at")


@admin.register(EducationRecord)
class EducationRecordAdmin(admin.ModelAdmin):
    list_display = ("record_type", "title", "issuer", "year", "status", "created_at")
    list_filter = ("record_type", "status")


@admin.register(PortfolioWork)
class PortfolioWorkAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "duration_minutes", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("client_name", "client_phone", "service", "starts_at", "status", "created_at")
    list_filter = ("status", "service")
    search_fields = ("client_name", "client_phone", "service__title")


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ("master", "opened_at", "closed_at", "status")
    list_filter = ("status",)


@admin.register(FinanceOperation)
class FinanceOperationAdmin(admin.ModelAdmin):
    list_display = ("operation_type", "title", "amount", "appointment", "shift", "created_at")
    list_filter = ("operation_type",)
