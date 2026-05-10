"""
api/main.py — Bütün SQLite əməliyyatlarını idarə edən tək FastAPI serveri.
Flet tərəfi artıq heç bir yerdə sqlite3 import etmir — hamısı bu API vasitəsilə gedir.

İstifadə:
    cd Project_Flet
    uvicorn api.main:app --reload --port 8000
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(title="AI Model Training Log API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB yolları ────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_REG         = os.path.join(BASE, "reg.db")
DB_EXPERIMENTS = os.path.join(BASE, "experiment.db")
DB_DATASETS    = os.path.join(BASE, "datasets.db")
DB_MODELS      = os.path.join(BASE, "models.db")
DB_REPORTS     = os.path.join(BASE, "reports.db")


def _conn(path: str) -> sqlite3.Connection:
    c = sqlite3.connect(path, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


# ════════════════════════════════════════════════════════════════════════════
#  USERS  (reg.db)
# ════════════════════════════════════════════════════════════════════════════

def _init_users():
    c = _conn(DB_REG)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'Data Scientist',
        status TEXT DEFAULT 'Active',
        joined TEXT
    )""")
    # migrate old tables
    cols = [r[1] for r in c.execute("PRAGMA table_info(users)").fetchall()]
    for col, defval in [("username","TEXT"), ("role","TEXT DEFAULT 'Data Scientist'"),
                        ("status","TEXT DEFAULT 'Active'"), ("joined","TEXT")]:
        if col not in cols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} {defval}")
    c.commit()
    c.close()

_init_users()

DEFAULT_USERS = [
    ("Dr. Sarah Chen",  "s.chen@aimodel.io",     "admin1234", "Admin",          "Active",   "2023-10-12"),
    ("Alex Rivera",     "a.rivera@aimodel.io",   "alex1234",  "Data Scientist", "Active",   "2023-11-05"),
    ("Jordan Smith",    "j.smith@aimodel.io",    "jordan1234","Viewer",         "Inactive", "2023-09-20"),
    ("Elena Rodriguez", "e.rodriguez@aimodel.io","elena1234", "Data Scientist", "Active",   "2023-12-01"),
    ("michael.ross",    "m.ross@aimodel.io",     "mike1234",  "Data Scientist", "Active",   "2023-11-28"),
]

def _seed_users():
    c = _conn(DB_REG)
    if c.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        for u in DEFAULT_USERS:
            try:
                c.execute("INSERT INTO users (username,email,password,role,status,joined) VALUES (?,?,?,?,?,?)", u)
            except sqlite3.IntegrityError:
                pass
    c.commit()
    c.close()

_seed_users()


class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "Data Scientist"

class UserUpdate(BaseModel):
    username: str
    email: str
    role: str
    status: str


@app.post("/auth/login")
def login(body: UserLogin):
    c = _conn(DB_REG)
    row = c.execute(
        "SELECT username, email, role FROM users WHERE email=? AND password=?",
        (body.email, body.password)
    ).fetchone()
    if not row:
        row = c.execute(
            "SELECT username, email, role FROM users WHERE LOWER(email)=LOWER(?) AND password=?",
            (body.email, body.password)
        ).fetchone()
    c.close()
    if not row:
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {"username": row["username"], "email": row["email"], "role": row["role"]}


@app.get("/users")
def get_users():
    c = _conn(DB_REG)
    rows = c.execute("SELECT id,username,email,role,status,joined FROM users ORDER BY id").fetchall()
    c.close()
    return [dict(r) for r in rows]


@app.post("/users")
def create_user(body: UserCreate):
    c = _conn(DB_REG)
    try:
        c.execute(
            "INSERT INTO users (username,email,password,role,status,joined) VALUES (?,?,?,?,?,?)",
            (body.username, body.email, body.password, body.role,
             "Active", datetime.now().strftime("%Y-%m-%d"))
        )
        c.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="This email already exists.")
    finally:
        c.close()
    return {"message": "User created."}


@app.put("/users/{uid}")
def update_user(uid: int, body: UserUpdate):
    c = _conn(DB_REG)
    cur = c.execute(
        "UPDATE users SET username=?, email=?, role=?, status=? WHERE id=?",
        (body.username, body.email, body.role, body.status, uid)
    )
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "Updated."}


@app.patch("/users/{uid}/status")
def toggle_status(uid: int, status: str):
    c = _conn(DB_REG)
    c.execute("UPDATE users SET status=? WHERE id=?", (status, uid))
    c.commit()
    c.close()
    return {"message": f"Status → {status}"}


@app.delete("/users/{uid}")
def delete_user(uid: int):
    c = _conn(DB_REG)
    cur = c.execute("DELETE FROM users WHERE id=?", (uid,))
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "Deleted."}


# ════════════════════════════════════════════════════════════════════════════
#  EXPERIMENTS  (experiment.db)
# ════════════════════════════════════════════════════════════════════════════

def _init_experiments():
    c = _conn(DB_EXPERIMENTS)
    c.execute("""CREATE TABLE IF NOT EXISTS experiments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exp_id TEXT UNIQUE, name TEXT NOT NULL, owner TEXT NOT NULL,
        model TEXT NOT NULL, created TEXT NOT NULL,
        status TEXT NOT NULL, description TEXT DEFAULT '')""")
    c.commit()
    c.close()

_init_experiments()

DEFAULT_EXPERIMENTS = [
    ("EXP-8802","ResNet-50 Image Classification","Alex Rivera","v2.4.0-alpha","2023-10-24\n14:22","Running","Fine-tuning ResNet50 on specialized medical imagery dataset."),
    ("EXP-8795","BERT Transformer Fine-tuning","Sarah Chen","v1.1.2-stable","2023-10-23\n09:15","Completed","BERT base model fine-tuned on SST-2 sentiment classification."),
    ("EXP-8782","YOLOv8 Object Detection - Dataset v2","Michael Park","v0.9.5-beta","2023-10-22\n18:40","Failed","Custom safety detection model using YOLOv8 architecture."),
    ("EXP-8777","LSTM Time-Series Forecasting","Alex Rivera","v3.0.1","2023-10-22\n11:05","Completed","LSTM-based stock price prediction with attention."),
    ("EXP-8761","Deep Reinforcement Learning - CartPole","Emma Wilson","v1.0.0","2023-10-21\n15:30","Completed","DQN agent trained on OpenAI CartPole-v1."),
]

def _seed_experiments():
    c = _conn(DB_EXPERIMENTS)
    for e in DEFAULT_EXPERIMENTS:
        c.execute("INSERT OR IGNORE INTO experiments (exp_id,name,owner,model,created,status,description) VALUES (?,?,?,?,?,?,?)", e)
    c.commit()
    c.close()

_seed_experiments()


class ExperimentCreate(BaseModel):
    exp_id: str
    name: str
    owner: str
    model: str
    created: str
    status: str
    description: str = ""

class ExperimentUpdate(BaseModel):
    name: str
    owner: str
    model: str
    status: str
    description: str = ""


@app.get("/experiments")
def get_experiments(search: Optional[str] = None):
    c = _conn(DB_EXPERIMENTS)
    if search:
        like = f"%{search}%"
        rows = c.execute(
            "SELECT exp_id,name,owner,model,created,status,description FROM experiments "
            "WHERE name LIKE ? OR exp_id LIKE ? OR model LIKE ? OR owner LIKE ? ORDER BY id DESC",
            (like, like, like, like)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT exp_id,name,owner,model,created,status,description FROM experiments ORDER BY id DESC"
        ).fetchall()
    c.close()
    return [{"id":r["exp_id"],"name":r["name"],"owner":r["owner"],
             "model":r["model"],"created":r["created"],"status":r["status"],
             "desc":r["description"] or ""} for r in rows]


@app.get("/experiments/next-id")
def next_experiment_id():
    c = _conn(DB_EXPERIMENTS)
    row = c.execute("SELECT MAX(id) FROM experiments").fetchone()
    c.close()
    return {"next_id": f"EXP-{9000+(row[0] or 0)+1}"}


@app.post("/experiments")
def create_experiment(body: ExperimentCreate):
    c = _conn(DB_EXPERIMENTS)
    c.execute(
        "INSERT INTO experiments (exp_id,name,owner,model,created,status,description) VALUES (?,?,?,?,?,?,?)",
        (body.exp_id, body.name, body.owner, body.model, body.created, body.status, body.description)
    )
    c.commit()
    c.close()
    return {"message": "Experiment created.", "exp_id": body.exp_id}


@app.put("/experiments/{exp_id}")
def update_experiment(exp_id: str, body: ExperimentUpdate):
    c = _conn(DB_EXPERIMENTS)
    cur = c.execute(
        "UPDATE experiments SET name=?,owner=?,model=?,status=?,description=? WHERE exp_id=?",
        (body.name, body.owner, body.model, body.status, body.description, exp_id)
    )
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return {"message": "Updated."}


@app.delete("/experiments/{exp_id}")
def delete_experiment(exp_id: str):
    c = _conn(DB_EXPERIMENTS)
    cur = c.execute("DELETE FROM experiments WHERE exp_id=?", (exp_id,))
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return {"message": "Deleted.", "exp_id": exp_id}


# ════════════════════════════════════════════════════════════════════════════
#  DATASETS  (datasets.db)
# ════════════════════════════════════════════════════════════════════════════

def _init_datasets():
    c = _conn(DB_DATASETS)
    c.execute("""CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, description TEXT, provider TEXT,
        size TEXT, created TEXT
    )""")
    c.commit()
    c.close()

_init_datasets()

DEFAULT_DATASETS = [
    ("ImageNet-1K-Sub","A subset of the ImageNet dataset focusing on common objects.","AWS S3 (US-East-1)","154.2 GB","2023-11-12"),
    ("CustomerChurn-2024","Aggregated anonymized customer behavior records.","GCP Bucket (Europe-West)","1.2 GB","2024-01-05"),
    ("NaturalLanguage-English","Large-scale corpus of web-scraped English text.","Azure Blob Storage","420.8 GB","2023-12-20"),
    ("MedicalScans-MRI-v2","Anonymized high-resolution MRI brain scans.","On-Premise NAS (Hospital A)","89.5 GB","2024-02-14"),
    ("AutonomousVehicles-Lidar","Multi-sensor lidar data recorded from urban environments.","AWS S3 (US-West-2)","1.5 TB","2024-03-01"),
]

def _seed_datasets():
    c = _conn(DB_DATASETS)
    if c.execute("SELECT COUNT(*) FROM datasets").fetchone()[0] == 0:
        for d in DEFAULT_DATASETS:
            c.execute("INSERT INTO datasets (name,description,provider,size,created) VALUES (?,?,?,?,?)", d)
    c.commit()
    c.close()

_seed_datasets()


class DatasetCreate(BaseModel):
    name: str
    description: str = ""
    provider: str
    size: str = "—"

class DatasetUpdate(BaseModel):
    name: str
    description: str = ""
    provider: str
    size: str = "—"


@app.get("/datasets")
def get_datasets(search: Optional[str] = None, provider: Optional[str] = None):
    c = _conn(DB_DATASETS)
    rows = c.execute("SELECT id,name,description,provider,size,created FROM datasets ORDER BY id").fetchall()
    c.close()
    data = [dict(r) for r in rows]
    if search:
        q = search.lower()
        data = [d for d in data if q in " ".join(str(d.get(k,"")) for k in ("name","description","provider","size")).lower()]
    if provider and provider != "All Providers":
        data = [d for d in data if d.get("provider") == provider]
    return data


@app.post("/datasets")
def create_dataset(body: DatasetCreate):
    c = _conn(DB_DATASETS)
    c.execute(
        "INSERT INTO datasets (name,description,provider,size,created) VALUES (?,?,?,?,?)",
        (body.name, body.description, body.provider, body.size, datetime.now().strftime("%Y-%m-%d"))
    )
    c.commit()
    c.close()
    return {"message": "Dataset added."}


@app.put("/datasets/{did}")
def update_dataset(did: int, body: DatasetUpdate):
    c = _conn(DB_DATASETS)
    cur = c.execute(
        "UPDATE datasets SET name=?,description=?,provider=?,size=? WHERE id=?",
        (body.name, body.description, body.provider, body.size, did)
    )
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"message": "Updated."}


@app.delete("/datasets/{did}")
def delete_dataset(did: int):
    c = _conn(DB_DATASETS)
    cur = c.execute("DELETE FROM datasets WHERE id=?", (did,))
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return {"message": "Deleted."}


# ════════════════════════════════════════════════════════════════════════════
#  MODELS  (models.db)
# ════════════════════════════════════════════════════════════════════════════

def _init_models():
    c = _conn(DB_MODELS)
    c.execute("""CREATE TABLE IF NOT EXISTS models (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        mod_id      TEXT UNIQUE,
        name        TEXT NOT NULL,
        version     TEXT NOT NULL,
        status      TEXT NOT NULL,
        dataset     TEXT DEFAULT '',
        experiment  TEXT DEFAULT '',
        created_at  TEXT DEFAULT '',
        notes       TEXT DEFAULT ''
    )""")
    c.commit()
    c.close()

_init_models()

DEFAULT_MODELS = [
    ("MOD-001","ResNet50-Object-Detection","v1.4.2","Completed","COCO-2017-val","Exp-942: Fine-tuning ResNet","2023-11-20 14:30","Optimized ResNet50 model for low-latency object detection on edge devices."),
    ("MOD-002","BERT-Large-NER","v2.1.0","Running","CoNLL-2003","Exp-938: BERT Finetuning","2023-11-21 09:15","BERT Large fine-tuned for named entity recognition."),
    ("MOD-003","UNet-MedSeg-v3","v3.0.0","Stopped","MedScans-MRI-v2","Exp-912: UNet Training","2023-11-18 16:45","UNet v3 trained on high-resolution MRI brain scans."),
    ("MOD-004","EfficientNet-B0-Food","v1.5.0","Stopped","Food-101-Clean","Exp-110: Custom Food Classif","2023-11-22 11:20","EfficientNet-B0 fine-tuned for 101-class food classification."),
    ("MOD-005","GPT2-FineTuned-Legal","v1.0.1","Completed","LegalCorpus-EN-2023","Exp-899: GPT2 Legal FT","2023-11-23 08:00","GPT-2 fine-tuned on English legal corpus for contract analysis."),
]

def _seed_models():
    c = _conn(DB_MODELS)
    if c.execute("SELECT COUNT(*) FROM models").fetchone()[0] == 0:
        for row in DEFAULT_MODELS:
            c.execute("INSERT OR IGNORE INTO models (mod_id,name,version,status,dataset,experiment,created_at,notes) VALUES (?,?,?,?,?,?,?,?)", row)
    c.commit()
    c.close()

_seed_models()


class ModelCreate(BaseModel):
    name: str
    version: str = "v1.0.0"
    status: str = "In Training"
    notes: str = ""

class ModelUpdate(BaseModel):
    name: str
    version: str
    status: str
    notes: str = ""


@app.get("/models")
def get_models(search: Optional[str] = None):
    c = _conn(DB_MODELS)
    rows = c.execute("SELECT mod_id,name,version,status,dataset,experiment,created_at,notes FROM models ORDER BY id").fetchall()
    c.close()
    data = [dict(r) for r in rows]
    if search:
        q = search.lower()
        data = [m for m in data if q in " ".join(str(m.get(k,"")) for k in ("name","mod_id","version","status","dataset","experiment","notes")).lower()]
    return data


@app.post("/models")
def create_model(body: ModelCreate):
    c = _conn(DB_MODELS)
    seq = (c.execute("SELECT MAX(id) FROM models").fetchone()[0] or 0) + 1
    mod_id = f"MOD-{seq:03d}"
    c.execute(
        "INSERT INTO models (mod_id,name,version,status,dataset,experiment,created_at,notes) VALUES (?,?,?,?,?,?,?,?)",
        (mod_id, body.name, body.version, body.status, "", "", datetime.now().strftime("%Y-%m-%d %H:%M"), body.notes)
    )
    c.commit()
    c.close()
    return {"message": "Model registered.", "mod_id": mod_id}


@app.put("/models/{mod_id}")
def update_model(mod_id: str, body: ModelUpdate):
    c = _conn(DB_MODELS)
    cur = c.execute(
        "UPDATE models SET name=?,version=?,status=?,notes=? WHERE mod_id=?",
        (body.name, body.version, body.status, body.notes, mod_id)
    )
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Model not found.")
    return {"message": "Updated."}


@app.delete("/models/{mod_id}")
def delete_model(mod_id: str):
    c = _conn(DB_MODELS)
    cur = c.execute("DELETE FROM models WHERE mod_id=?", (mod_id,))
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Model not found.")
    return {"message": "Deleted."}


# ════════════════════════════════════════════════════════════════════════════
#  REPORTS  (reports.db)
# ════════════════════════════════════════════════════════════════════════════

def _init_reports():
    c = _conn(DB_REPORTS)
    c.execute("""CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, format TEXT, experiment TEXT,
        creator TEXT, created_at TEXT, status TEXT
    )""")
    c.commit()
    c.close()

_init_reports()

DEFAULT_REPORTS = [
    ("Q3 ResNet-50 Training Summary","PDF","EXP-902","Jordan Smith","2023-10-24 14:30","Final"),
    ("BERT-Large Optimization Results","HTML","EXP-884","Sarah Chen","2023-10-22 09:15","Final"),
    ("Image-Seg-V2 Performance Audit","PDF","EXP-905","Jordan Smith","2023-10-21 16:45","Draft"),
    ("Hyperparameter Tuning: Learning Rate","PDF","EXP-772","Marcus Vogt","2023-10-18 11:00","Final"),
    ("ViT-Base Baseline Evaluation","HTML","EXP-651","Jordan Smith","2023-10-15 13:20","Final"),
]

def _seed_reports():
    c = _conn(DB_REPORTS)
    if c.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 0:
        for row in DEFAULT_REPORTS:
            c.execute("INSERT INTO reports (title,format,experiment,creator,created_at,status) VALUES (?,?,?,?,?,?)", row)
    c.commit()
    c.close()

_seed_reports()


class ReportCreate(BaseModel):
    title: str
    format: str = "PDF"
    experiment: str
    creator: str
    status: str = "Draft"

class ReportUpdate(BaseModel):
    title: str
    format: str
    experiment: str
    status: str


@app.get("/reports")
def get_reports(search: Optional[str] = None, format: Optional[str] = None):
    c = _conn(DB_REPORTS)
    rows = c.execute("SELECT id,title,format,experiment,creator,created_at,status FROM reports ORDER BY id DESC").fetchall()
    c.close()
    data = [dict(r) for r in rows]
    if format and format != "All":
        data = [r for r in data if r.get("format") == format]
    if search:
        q = search.lower()
        data = [r for r in data if q in " ".join(str(r.get(k,"")) for k in ("title","format","experiment","creator","status")).lower()]
    return data


@app.post("/reports")
def create_report(body: ReportCreate):
    c = _conn(DB_REPORTS)
    c.execute(
        "INSERT INTO reports (title,format,experiment,creator,created_at,status) VALUES (?,?,?,?,?,?)",
        (body.title, body.format, body.experiment, body.creator,
         datetime.now().strftime("%Y-%m-%d %H:%M"), body.status)
    )
    c.commit()
    c.close()
    return {"message": "Report created."}


@app.put("/reports/{rid}")
def update_report(rid: int, body: ReportUpdate):
    c = _conn(DB_REPORTS)
    cur = c.execute(
        "UPDATE reports SET title=?,format=?,experiment=?,status=? WHERE id=?",
        (body.title, body.format, body.experiment, body.status, rid)
    )
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"message": "Updated."}


@app.delete("/reports/{rid}")
def delete_report(rid: int):
    c = _conn(DB_REPORTS)
    cur = c.execute("DELETE FROM reports WHERE id=?", (rid,))
    c.commit()
    c.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Report not found.")
    return {"message": "Deleted."}


# ════════════════════════════════════════════════════════════════════════════
#  DELETE ALL  (Homework — Lab 10)
# ════════════════════════════════════════════════════════════════════════════

@app.delete("/experiments")
def delete_all_experiments():
    c = _conn(DB_EXPERIMENTS)
    c.execute("DELETE FROM experiments")
    c.commit()
    c.close()
    return {"message": "All experiments deleted."}


@app.delete("/datasets")
def delete_all_datasets():
    c = _conn(DB_DATASETS)
    c.execute("DELETE FROM datasets")
    c.commit()
    c.close()
    return {"message": "All datasets deleted."}


@app.delete("/models")
def delete_all_models():
    c = _conn(DB_MODELS)
    c.execute("DELETE FROM models")
    c.commit()
    c.close()
    return {"message": "All models deleted."}


@app.delete("/reports")
def delete_all_reports():
    c = _conn(DB_REPORTS)
    c.execute("DELETE FROM reports")
    c.commit()
    c.close()
    return {"message": "All reports deleted."}


# ════════════════════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════════
@app.get("/")
def health():
    return {"status": "ok", "message": "AI Model Training Log API is running."}
