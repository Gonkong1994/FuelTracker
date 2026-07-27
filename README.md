# FuelTracker

REST API для управления заправками автомобилей и подсчета количества денежных средств.

## 🛠 Стек

- **Python 3.11** + **FastAPI**
- **Pydantic** (валидация данных)
- **PostgreSQL** + **SQLAlchemy ORM**
- **Docker** + **Docker Compose**

## 🚀 Быстрый запуск

```bash
git clone https://github.com/Gonkong1994/FuelTracker.git
cd FuelTracker
docker compose up
```

## 📂 Структура проекта

├── app.py               # REST API (FastAPI)
├── fuel.py              # Pydantic-модель FuelUp
├── storage.py           # SQLAlchemy ORM + PostgreSQL
├── Dockerfile           # Сборка контейнера
├── docker-compose.yml   # Запуск app + PostgreSQL
├── requirements.txt     # Зависимости
└── .gitignore

## 📋 API (CRUD)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/fuelups` | Список всех заправок |
| GET | `/fuelups/{id}` | Поиск по ID |
| GET | `/fuelups/stats` | Статистика (всего литров, сумма) |
| POST | `/fuelups` | Добавить заправку |
| PUT | `/fuelups/{id}` | Обновить заправку |
| DELETE | `/fuelups/{id}` | Удалить заправку |

## 🧪 Запуск без Docker

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app:app --reload
```