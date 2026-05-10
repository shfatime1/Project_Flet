"""
api/client.py — Bütün Flet view-larının istifadə etdiyi API klient.
Bu fayl sqlite3 importunu tamamilə əvəz edir.
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def _get(path: str, params: dict = None):
    r = requests.get(f"{BASE_URL}{path}", params=params or {})
    r.raise_for_status()
    return r.json()


def _post(path: str, data: dict):
    r = requests.post(f"{BASE_URL}{path}", json=data)
    r.raise_for_status()
    return r.json()


def _put(path: str, data: dict):
    r = requests.put(f"{BASE_URL}{path}", json=data)
    r.raise_for_status()
    return r.json()


def _patch(path: str, params: dict = None):
    r = requests.patch(f"{BASE_URL}{path}", params=params or {})
    r.raise_for_status()
    return r.json()


def _delete(path: str):
    r = requests.delete(f"{BASE_URL}{path}")
    r.raise_for_status()
    return r.json()


# ── Auth ──────────────────────────────────────────────────────────────────────
def login(email: str, password: str) -> dict:
    """Returns {username, email, role} or raises HTTPError (401)."""
    return _post("/auth/login", {"email": email, "password": password})


# ── Users ─────────────────────────────────────────────────────────────────────
def get_users() -> list:
    return _get("/users")

def create_user(username: str, email: str, password: str,
                role: str = "Data Scientist") -> dict:
    return _post("/users", {"username": username, "email": email,
                            "password": password, "role": role})

def update_user(uid: int, username: str, email: str,
                role: str, status: str) -> dict:
    return _put(f"/users/{uid}", {"username": username, "email": email,
                                  "role": role, "status": status})

def toggle_user_status(uid: int, new_status: str) -> dict:
    return _patch(f"/users/{uid}/status", {"status": new_status})

def delete_user(uid: int) -> dict:
    return _delete(f"/users/{uid}")


# ── Experiments ───────────────────────────────────────────────────────────────
def get_experiments(search: str = "") -> list:
    params = {"search": search} if search else {}
    return _get("/experiments", params)

def get_next_experiment_id() -> str:
    return _get("/experiments/next-id")["next_id"]

def create_experiment(exp_id: str, name: str, owner: str, model: str,
                      created: str, status: str, description: str = "") -> dict:
    return _post("/experiments", {"exp_id": exp_id, "name": name,
                                  "owner": owner, "model": model,
                                  "created": created, "status": status,
                                  "description": description})

def update_experiment(exp_id: str, name: str, owner: str, model: str,
                      status: str, description: str = "") -> dict:
    return _put(f"/experiments/{exp_id}", {"name": name, "owner": owner,
                                            "model": model, "status": status,
                                            "description": description})

def delete_experiment(exp_id: str) -> dict:
    return _delete(f"/experiments/{exp_id}")


# ── Datasets ──────────────────────────────────────────────────────────────────
def get_datasets(search: str = "", provider: str = "") -> list:
    params = {}
    if search:
        params["search"] = search
    if provider and provider != "All Providers":
        params["provider"] = provider
    return _get("/datasets", params)

def create_dataset(name: str, description: str, provider: str, size: str) -> dict:
    return _post("/datasets", {"name": name, "description": description,
                               "provider": provider, "size": size})

def update_dataset(did: int, name: str, description: str,
                   provider: str, size: str) -> dict:
    return _put(f"/datasets/{did}", {"name": name, "description": description,
                                     "provider": provider, "size": size})

def delete_dataset(did: int) -> dict:
    return _delete(f"/datasets/{did}")


# ── Models ────────────────────────────────────────────────────────────────────
def get_models(search: str = "") -> list:
    params = {"search": search} if search else {}
    return _get("/models", params)

def create_model(name: str, version: str = "v1.0.0",
                 status: str = "In Training", notes: str = "") -> dict:
    return _post("/models", {"name": name, "version": version,
                             "status": status, "notes": notes})

def update_model(mod_id: str, name: str, version: str,
                 status: str, notes: str = "") -> dict:
    return _put(f"/models/{mod_id}", {"name": name, "version": version,
                                      "status": status, "notes": notes})

def delete_model(mod_id: str) -> dict:
    return _delete(f"/models/{mod_id}")


# ── Reports ───────────────────────────────────────────────────────────────────
def get_reports(search: str = "", format: str = "") -> list:
    params = {}
    if search:
        params["search"] = search
    if format and format != "All":
        params["format"] = format
    return _get("/reports", params)

def create_report(title: str, format: str, experiment: str,
                  creator: str, status: str = "Draft") -> dict:
    return _post("/reports", {"title": title, "format": format,
                              "experiment": experiment, "creator": creator,
                              "status": status})

def update_report(rid: int, title: str, format: str,
                  experiment: str, status: str) -> dict:
    return _put(f"/reports/{rid}", {"title": title, "format": format,
                                    "experiment": experiment, "status": status})

def delete_report(rid: int) -> dict:
    return _delete(f"/reports/{rid}")


# ── Delete All (Homework — Lab 10) ────────────────────────────────────────────
def delete_all_experiments() -> dict:
    return _delete("/experiments")

def delete_all_datasets() -> dict:
    return _delete("/datasets")

def delete_all_models() -> dict:
    return _delete("/models")

def delete_all_reports() -> dict:
    return _delete("/reports")
