# API Qovluğu — AI Model Training Log

Bu qovluq bütün SQLite əməliyyatlarını idarə edən FastAPI serverini özündə saxlayır.

## Fayllar

| Fayl | Məqsəd |
|------|--------|
| `api/main.py` | FastAPI server — bütün endpoint-lər (CRUD) |
| `api/client.py` | Flet view-larının istifadə etdiyi Python API klienti |
| `api/__init__.py` | Python paketi kimi tanıtmaq üçün |

## Serveri işə salmaq

```bash
cd Project_Flet
uvicorn api.main:app --reload --port 8000
```

Sonra ayrı terminalda:

```bash
python main.py
```

## Swagger UI

Server işlədikdə: http://127.0.0.1:8000/docs

## Endpoint-lər

### Auth
- `POST /auth/login` — email + password ilə giriş

### Users (`reg.db`)
- `GET  /users`
- `POST /users`
- `PUT  /users/{uid}`
- `PATCH /users/{uid}/status?status=Active`
- `DELETE /users/{uid}`

### Experiments (`experiment.db`)
- `GET  /experiments?search=...`
- `GET  /experiments/next-id`
- `POST /experiments`
- `PUT  /experiments/{exp_id}`
- `DELETE /experiments/{exp_id}`

### Datasets (`datasets.db`)
- `GET  /datasets?search=...&provider=...`
- `POST /datasets`
- `PUT  /datasets/{did}`
- `DELETE /datasets/{did}`

### Models (`models.db`)
- `GET  /models?search=...`
- `POST /models`
- `PUT  /models/{mod_id}`
- `DELETE /models/{mod_id}`

### Reports (`reports.db`)
- `GET  /reports?search=...&format=PDF`
- `POST /reports`
- `PUT  /reports/{rid}`
- `DELETE /reports/{rid}`
