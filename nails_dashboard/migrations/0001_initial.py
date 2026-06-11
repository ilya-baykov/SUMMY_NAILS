from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="EducationRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("record_type", models.CharField(choices=[("diploma", "Диплом"), ("course", "Курс"), ("certificate", "Сертификат")], max_length=16)),
                ("title", models.CharField(max_length=160)),
                ("issuer", models.CharField(max_length=160)),
                ("year", models.PositiveSmallIntegerField()),
                ("status", models.CharField(choices=[("confirmed", "Подтверждено"), ("review", "На проверке")], default="review", max_length=16)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Образование и курс",
                "verbose_name_plural": "Образование и курсы",
                "ordering": ["-created_at", "-id"],
            },
        ),
        migrations.CreateModel(
            name="MedicalBook",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=80)),
                ("valid_until", models.DateField()),
                ("status", models.CharField(choices=[("valid", "Действительна"), ("review", "На проверке"), ("expired", "Истек срок")], default="valid", max_length=16)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Медицинская книжка",
                "verbose_name_plural": "Медицинские книжки",
            },
        ),
        migrations.CreateModel(
            name="PortfolioWork",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=120)),
                ("image", models.FileField(upload_to="portfolio/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Работа в портфолио",
                "verbose_name_plural": "Работы в портфолио",
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
