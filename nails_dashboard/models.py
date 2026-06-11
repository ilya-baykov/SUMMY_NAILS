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
