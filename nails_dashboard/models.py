from django.conf import settings
from django.db import models


class MedicalBook(models.Model):
    STATUS_VALID = "valid"
    STATUS_REVIEW = "review"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_VALID, "Действительна"),
        (STATUS_REVIEW, "На проверке"),
        (STATUS_EXPIRED, "Истек срок"),
    ]

    number = models.CharField(max_length=80)
    valid_until = models.DateField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_VALID)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Медицинская книжка"
        verbose_name_plural = "Медицинские книжки"

    def __str__(self):
        return self.number


class EducationRecord(models.Model):
    TYPE_DIPLOMA = "diploma"
    TYPE_COURSE = "course"
    TYPE_CERTIFICATE = "certificate"

    TYPE_CHOICES = [
        (TYPE_DIPLOMA, "Диплом"),
        (TYPE_COURSE, "Курс"),
        (TYPE_CERTIFICATE, "Сертификат"),
    ]

    STATUS_CONFIRMED = "confirmed"
    STATUS_REVIEW = "review"

    STATUS_CHOICES = [
        (STATUS_CONFIRMED, "Подтверждено"),
        (STATUS_REVIEW, "На проверке"),
    ]

    record_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    title = models.CharField(max_length=160)
    issuer = models.CharField(max_length=160)
    year = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_REVIEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Образование и курс"
        verbose_name_plural = "Образование и курсы"

    def __str__(self):
        return f"{self.get_record_type_display()} · {self.title}"


class PortfolioWork(models.Model):
    title = models.CharField(max_length=120)
    image = models.FileField(upload_to="portfolio/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Работа в портфолио"
        verbose_name_plural = "Работы в портфолио"

    def __str__(self):
        return self.title


class Service(models.Model):
    title = models.CharField(max_length=120)
    duration_minutes = models.PositiveSmallIntegerField(default=90)
    price = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.title


class Appointment(models.Model):
    STATUS_NEW = "new"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CLOSED = "closed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_NEW, "Новая"),
        (STATUS_CONFIRMED, "Подтверждена"),
        (STATUS_CLOSED, "Закрыта"),
        (STATUS_CANCELLED, "Отменена"),
    ]

    client_name = models.CharField(max_length=120)
    client_phone = models.CharField(max_length=40)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    starts_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_NEW)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["starts_at", "id"]
        verbose_name = "Запись"
        verbose_name_plural = "Записи"

    def __str__(self):
        return f"{self.client_name} · {self.service}"


class Shift(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Открыта"),
        (STATUS_CLOSED, "Закрыта"),
    ]

    master = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="shifts")
    opened_at = models.DateTimeField()
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)

    class Meta:
        ordering = ["-opened_at"]
        verbose_name = "Смена"
        verbose_name_plural = "Смены"

    def __str__(self):
        return f"{self.get_status_display()} · {self.opened_at:%d.%m.%Y}"


class FinanceOperation(models.Model):
    TYPE_ACCRUAL = "accrual"
    TYPE_PAYOUT = "payout"
    TYPE_ADJUSTMENT = "adjustment"

    TYPE_CHOICES = [
        (TYPE_ACCRUAL, "Начисление"),
        (TYPE_PAYOUT, "Выплата"),
        (TYPE_ADJUSTMENT, "Корректировка"),
    ]

    operation_type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    title = models.CharField(max_length=160)
    amount = models.IntegerField()
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name="finance_operation")
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True, related_name="finance_operations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "Финансовая операция"
        verbose_name_plural = "Финансовые операции"

    def __str__(self):
        return f"{self.get_operation_type_display()} · {self.amount}"
