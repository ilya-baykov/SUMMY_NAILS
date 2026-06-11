import json
from datetime import date

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods, require_POST

from .models import EducationRecord, MedicalBook, PortfolioWork


def dashboard(request):
    ensure_initial_data()
    return render(request, "dashboard/index.html")


@require_http_methods(["GET", "POST"])
def profile_api(request):
    medical_book = get_medical_book()

    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        medical_book.number = payload["number"].strip()
        medical_book.valid_until = payload["valid_until"]
        medical_book.status = payload["status"]
        medical_book.save()

    return JsonResponse(
        {
            "medical_book": serialize_medical_book(medical_book),
            "education": [serialize_education(record) for record in EducationRecord.objects.all()],
            "portfolio": [serialize_work(work) for work in PortfolioWork.objects.all()],
        }
    )


@require_POST
def education_create_api(request):
    record = EducationRecord.objects.create(
        record_type=request.POST["record_type"],
        title=request.POST["title"].strip(),
        issuer=request.POST["issuer"].strip(),
        year=int(request.POST["year"]),
        status=request.POST["status"],
    )

    return JsonResponse(serialize_education(record), status=201)


@require_http_methods(["DELETE"])
def education_delete_api(request, record_id):
    record = get_object_or_404(EducationRecord, pk=record_id)
    record.delete()
    return JsonResponse({"ok": True})


@require_POST
def portfolio_create_api(request):
    work = PortfolioWork.objects.create(
        title=request.POST["title"].strip(),
        image=request.FILES["image"],
    )

    return JsonResponse(serialize_work(work), status=201)


@require_http_methods(["DELETE"])
def portfolio_delete_api(request, work_id):
    work = get_object_or_404(PortfolioWork, pk=work_id)
    work.image.delete(save=False)
    work.delete()
    return JsonResponse({"ok": True})


def get_medical_book():
    return MedicalBook.objects.first() or MedicalBook.objects.create(
        number="77 МК 0482913",
        valid_until=date(2026, 11, 14),
        status=MedicalBook.STATUS_VALID,
    )


def ensure_initial_data():
    get_medical_book()

    if not EducationRecord.objects.exists():
        EducationRecord.objects.bulk_create(
            [
                EducationRecord(record_type=EducationRecord.TYPE_DIPLOMA, title="Технолог ногтевого сервиса", issuer="Академия «Эстель»", year=2021, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Аппаратный маникюр PRO", issuer="Nail Expert School", year=2024, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Сложные дизайны и френч", issuer="SUMMY Lab", year=2025, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Дезинфекция и стерилизация", issuer="Учебный центр «Гигиена+»", year=2025, status=EducationRecord.STATUS_REVIEW),
            ]
        )


def serialize_medical_book(medical_book):
    return {
        "id": medical_book.id,
        "number": medical_book.number,
        "valid_until": medical_book.valid_until.isoformat(),
        "valid_until_display": medical_book.valid_until.strftime("%d.%m.%Y"),
        "status": medical_book.status,
        "status_display": medical_book.get_status_display(),
    }


def serialize_education(record):
    return {
        "id": record.id,
        "record_type": record.record_type,
        "record_type_display": record.get_record_type_display(),
        "title": record.title,
        "issuer": record.issuer,
        "year": record.year,
        "status": record.status,
        "status_display": record.get_status_display(),
    }


def serialize_work(work):
    return {
        "id": work.id,
        "title": work.title,
        "image_url": work.image.url,
    }
