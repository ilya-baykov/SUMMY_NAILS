from django.contrib import admin

from .models import EducationRecord, MedicalBook, PortfolioWork


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
