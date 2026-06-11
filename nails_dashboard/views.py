import json
from datetime import date, datetime, time, timedelta

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .models import Appointment, EducationRecord, FinanceOperation, MedicalBook, PortfolioWork, Service, Shift


ROLE_MASTER = "master"
ROLE_ADMIN = "admin"
ROLE_OWNER = "owner"
ROLE_LABELS = {
    ROLE_MASTER: "Мастер",
    ROLE_ADMIN: "Администратор",
    ROLE_OWNER: "Владелец",
}


def can_manage(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=[ROLE_ADMIN, ROLE_OWNER]).exists())


def can_owner(user):
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name=ROLE_OWNER).exists())


def get_role_label(user):
    if not user.is_authenticated:
        return ""

    if user.is_superuser:
        return "Владелец"

    for role, label in ROLE_LABELS.items():
        if user.groups.filter(name=role).exists():
            return label

    return "Мастер"


def login_page(request):
    ensure_initial_data()

    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    error = ""

    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])

        if user:
            login(request, user)
            return redirect("dashboard:dashboard")

        error = "Неверный логин или пароль"

    return render(request, "dashboard/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("dashboard:login")


@login_required
def dashboard(request):
    ensure_initial_data()
    return render(
        request,
        "dashboard/index.html",
        {
            "can_manage": can_manage(request.user),
            "role_label": get_role_label(request.user),
        },
    )


def booking_page(request):
    ensure_initial_data()
    return render(request, "dashboard/booking.html")


@login_required
@user_passes_test(can_manage)
def staff_panel(request):
    ensure_initial_data()
    return render(request, "dashboard/staff.html", {"role_label": get_role_label(request.user), "can_owner": can_owner(request.user)})


@login_required
@require_http_methods(["GET"])
def dashboard_api(request):
    ensure_initial_data()
    medical_book = get_medical_book()

    return JsonResponse(
        {
            "user": {
                "username": request.user.username,
                "role": get_role_label(request.user),
                "can_manage": can_manage(request.user),
            },
            "medical_book": serialize_medical_book(medical_book),
            "education": [serialize_education(record) for record in EducationRecord.objects.all()],
            "portfolio": [serialize_work(work) for work in PortfolioWork.objects.all()],
            "appointments": [serialize_appointment(record) for record in Appointment.objects.select_related("service").all()],
            "shift": serialize_shift(get_current_shift()),
            "finance": serialize_finance_summary(),
            "services": [serialize_service(service) for service in Service.objects.filter(is_active=True)],
        }
    )


@login_required
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


@login_required
@require_POST
def shift_toggle_api(request):
    current_shift = get_current_shift()

    if current_shift:
        current_shift.status = Shift.STATUS_CLOSED
        current_shift.closed_at = timezone.now()
        current_shift.save()
        return JsonResponse(serialize_shift(None))

    shift = Shift.objects.create(master=request.user, opened_at=timezone.now(), status=Shift.STATUS_OPEN)
    return JsonResponse(serialize_shift(shift), status=201)


@login_required
@require_POST
def appointment_close_api(request, appointment_id):
    appointment = get_object_or_404(Appointment.objects.select_related("service"), pk=appointment_id)
    appointment.status = Appointment.STATUS_CLOSED
    appointment.save()

    shift = get_current_shift()
    FinanceOperation.objects.get_or_create(
        appointment=appointment,
        defaults={
            "operation_type": FinanceOperation.TYPE_ACCRUAL,
            "title": f"Начисление · {appointment.client_name}",
            "amount": round(appointment.service.price * 0.45),
            "shift": shift,
        },
    )

    return JsonResponse(
        {
            "appointment": serialize_appointment(appointment),
            "shift": serialize_shift(shift),
            "finance": serialize_finance_summary(),
        }
    )


@login_required
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


@login_required
@require_http_methods(["DELETE"])
def education_delete_api(request, record_id):
    record = get_object_or_404(EducationRecord, pk=record_id)
    record.delete()
    return JsonResponse({"ok": True})


@login_required
@require_POST
def portfolio_create_api(request):
    work = PortfolioWork.objects.create(
        title=request.POST["title"].strip(),
        image=request.FILES["image"],
    )

    return JsonResponse(serialize_work(work), status=201)


@login_required
@require_http_methods(["DELETE"])
def portfolio_delete_api(request, work_id):
    work = get_object_or_404(PortfolioWork, pk=work_id)
    work.image.delete(save=False)
    work.delete()
    return JsonResponse({"ok": True})


@require_http_methods(["GET", "POST"])
def public_booking_api(request):
    ensure_initial_data()

    if request.method == "GET":
        return JsonResponse({"services": [serialize_service(service) for service in Service.objects.filter(is_active=True)]})

    appointment = Appointment.objects.create(
        client_name=request.POST["client_name"].strip(),
        client_phone=request.POST["client_phone"].strip(),
        service=get_object_or_404(Service, pk=request.POST["service_id"], is_active=True),
        starts_at=parse_local_datetime(request.POST["starts_at"]),
        notes=request.POST.get("notes", "").strip(),
        status=Appointment.STATUS_NEW,
    )

    return JsonResponse(serialize_appointment(appointment), status=201)


@login_required
@user_passes_test(can_manage)
@require_http_methods(["GET"])
def manage_api(request):
    return JsonResponse(
        {
            "services": [serialize_service(service) for service in Service.objects.all()],
            "appointments": [serialize_appointment(record) for record in Appointment.objects.select_related("service").all()],
            "finance": serialize_finance_summary(),
        }
    )


@login_required
@user_passes_test(can_manage)
@require_POST
def service_create_api(request):
    service = Service.objects.create(
        title=request.POST["title"].strip(),
        duration_minutes=int(request.POST["duration_minutes"]),
        price=int(request.POST["price"]),
        is_active=True,
    )
    return JsonResponse(serialize_service(service), status=201)


@login_required
@user_passes_test(can_manage)
@require_http_methods(["DELETE"])
def service_delete_api(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    service.is_active = False
    service.save()
    return JsonResponse({"ok": True})


@login_required
@user_passes_test(can_manage)
@require_POST
def staff_appointment_create_api(request):
    appointment = Appointment.objects.create(
        client_name=request.POST["client_name"].strip(),
        client_phone=request.POST["client_phone"].strip(),
        service=get_object_or_404(Service, pk=request.POST["service_id"]),
        starts_at=parse_local_datetime(request.POST["starts_at"]),
        notes=request.POST.get("notes", "").strip(),
        status=request.POST["status"],
    )
    return JsonResponse(serialize_appointment(appointment), status=201)


@login_required
@user_passes_test(can_owner)
@require_POST
def payout_create_api(request):
    operation = FinanceOperation.objects.create(
        operation_type=FinanceOperation.TYPE_PAYOUT,
        title=request.POST["title"].strip(),
        amount=-abs(int(request.POST["amount"])),
    )
    return JsonResponse(serialize_finance_operation(operation), status=201)


def get_medical_book():
    return MedicalBook.objects.first() or MedicalBook.objects.create(
        number="77 МК 0482913",
        valid_until=date(2026, 11, 14),
        status=MedicalBook.STATUS_VALID,
    )


def get_current_shift():
    return Shift.objects.filter(status=Shift.STATUS_OPEN).first()


def ensure_initial_data():
    create_roles_and_users()
    get_medical_book()
    create_default_services()
    create_default_appointments()

    if not EducationRecord.objects.exists():
        EducationRecord.objects.bulk_create(
            [
                EducationRecord(record_type=EducationRecord.TYPE_DIPLOMA, title="Технолог ногтевого сервиса", issuer="Академия «Эстель»", year=2021, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Аппаратный маникюр PRO", issuer="Nail Expert School", year=2024, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Сложные дизайны и френч", issuer="SUMMY Lab", year=2025, status=EducationRecord.STATUS_CONFIRMED),
                EducationRecord(record_type=EducationRecord.TYPE_COURSE, title="Дезинфекция и стерилизация", issuer="Учебный центр «Гигиена+»", year=2025, status=EducationRecord.STATUS_REVIEW),
            ]
        )


def create_roles_and_users():
    for role in ROLE_LABELS:
        Group.objects.get_or_create(name=role)

    users = [
        ("master", ROLE_MASTER, False, False),
        ("admin", ROLE_ADMIN, True, False),
        ("owner", ROLE_OWNER, True, True),
    ]

    for username, role, is_staff, is_superuser in users:
        user, created = User.objects.get_or_create(username=username, defaults={"is_staff": is_staff, "is_superuser": is_superuser})

        if created:
            user.set_password("demo12345")
            user.save()

        user.groups.add(Group.objects.get(name=role))


def create_default_services():
    if Service.objects.exists():
        return

    Service.objects.bulk_create(
        [
            Service(title="Маникюр + покрытие гель-лак", duration_minutes=120, price=3200),
            Service(title="Снятие + укрепление + дизайн", duration_minutes=150, price=4100),
            Service(title="Маникюр комбинированный", duration_minutes=90, price=2400),
            Service(title="Френч + ремонт 2 ногтей", duration_minutes=130, price=3600),
        ]
    )


def create_default_appointments():
    if Appointment.objects.exists():
        return

    services = list(Service.objects.all())
    today = timezone.localdate()
    times = [time(10, 0), time(12, 30), time(15, 30), time(17, 30)]
    clients = ["Мария С.", "Ольга Д.", "Виктория П.", "Елена Т."]

    for index, service in enumerate(services[:4]):
        starts_at = timezone.make_aware(datetime.combine(today, times[index]))
        Appointment.objects.create(
            client_name=clients[index],
            client_phone="+7 900 000-00-0" + str(index + 1),
            service=service,
            starts_at=starts_at,
            status=Appointment.STATUS_CONFIRMED,
        )


def parse_local_datetime(value):
    parsed = datetime.fromisoformat(value)

    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed)

    return parsed


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


def serialize_service(service):
    return {
        "id": service.id,
        "title": service.title,
        "duration_minutes": service.duration_minutes,
        "price": service.price,
        "is_active": service.is_active,
    }


def serialize_appointment(appointment):
    return {
        "id": appointment.id,
        "client_name": appointment.client_name,
        "client_phone": appointment.client_phone,
        "service": serialize_service(appointment.service),
        "starts_at": appointment.starts_at.isoformat(),
        "date_display": timezone.localtime(appointment.starts_at).strftime("%d.%m.%Y"),
        "time_display": timezone.localtime(appointment.starts_at).strftime("%H:%M"),
        "status": appointment.status,
        "status_display": appointment.get_status_display(),
        "notes": appointment.notes,
    }


def serialize_shift(shift):
    if not shift:
        return {"is_open": False, "status_display": "Смена закрыта", "opened_at": None, "closed_at": None}

    return {
        "id": shift.id,
        "is_open": shift.status == Shift.STATUS_OPEN,
        "status_display": shift.get_status_display(),
        "opened_at": timezone.localtime(shift.opened_at).strftime("%d.%m.%Y %H:%M"),
        "closed_at": timezone.localtime(shift.closed_at).strftime("%d.%m.%Y %H:%M") if shift.closed_at else None,
    }


def serialize_finance_summary():
    operations = list(FinanceOperation.objects.all())
    balance = sum(operation.amount for operation in operations)

    return {
        "balance": balance,
        "operations": [serialize_finance_operation(operation) for operation in operations],
    }


def serialize_finance_operation(operation):
    return {
        "id": operation.id,
        "operation_type": operation.operation_type,
        "operation_type_display": operation.get_operation_type_display(),
        "title": operation.title,
        "amount": operation.amount,
        "created_at_display": timezone.localtime(operation.created_at).strftime("%d.%m.%Y, %H:%M"),
    }
