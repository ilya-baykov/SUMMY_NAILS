# Nails Pro

Django MVP личного кабинета мастера ногтевого сервиса.

## Стек

- Django
- SQLite для локальной разработки
- Django templates + static CSS/JS
- Загруженные фото портфолио хранятся в `uploads/`

## Запуск

```bash
uv run python manage.py migrate
uv run python manage.py runserver 127.0.0.1:8765
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:8765/
```

## Что уже есть

- Авторизация через Django auth
- Демо-роли `master`, `admin`, `owner`
- Открытие и закрытие смены через Django model `Shift`
- Список записей из Django model `Appointment`
- Закрытие записи с созданием финансового начисления
- Редактирование медицинской книжки через Django API
- Добавление и удаление записей образования и курсов
- Добавление и удаление работ портфолио с загрузкой фото
- Собственная публичная онлайн-запись на `/booking/`
- Управленческая панель на `/staff/` для услуг, расписания и выплат
- Хранение профиля, расписания, смен, услуг, портфолио и финансов в SQLite
- Базовая Django admin-регистрация моделей

## Демо-доступы

```text
master / demo12345
admin / demo12345
owner / demo12345
```

`master` работает с личным кабинетом. `admin` видит управленческую панель услуг и расписания. `owner` дополнительно может проводить выплаты.

## Структура

- `nails_project/` — настройки Django-проекта
- `nails_dashboard/` — приложение личного кабинета
- `nails_dashboard/templates/dashboard/index.html` — основной экран
- `nails_dashboard/static/dashboard/` — CSS и JavaScript
- `nails_dashboard/models.py` — модели медицинской книжки, образования, портфолио, услуг, записей, смен и финансов
- `uploads/` — пользовательские загрузки, создается при загрузке фото

## Следующие задачи

- Перенести демо-данные из runtime-seed в fixtures или management command
- Добавить редактирование и отмену записей в staff-панели
- Добавить календарную сетку свободных слотов
- Подготовить production-настройки `SECRET_KEY`, `ALLOWED_HOSTS`, static/media storage
