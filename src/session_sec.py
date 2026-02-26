import json
import os
import hashlib
import time
import streamlit as st

TRACKER_FILE = "limit_tracker.json"
MAX_RUNS_PER_SESSION = 3

# Hash"
SECRET_CODE_HASH = "ebec6f726fee7a9baf75628bcb9b0dec4d219f097f5c8c4cb91fc4495e6c1f83"

def _get_client_ip() -> str:
    """Intenta conseguir la IP real del cliente, usando los headers de Streamlit >= 1.39"""
    try:
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers
            forwarded_for = headers.get("X-Forwarded-For")
            if forwarded_for:
                return forwarded_for.split(",")[0].strip()
            real_ip = headers.get("X-Real-IP")
            if real_ip:
                return real_ip.strip()
    except Exception:
        pass
        
    # Fallback clásico
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        ctx = get_script_run_ctx()
        if ctx:
            return ctx.session_id
    except Exception:
        pass

    return "unknown_client"

def _load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_tracker(data: dict):
    try:
        with open(TRACKER_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def is_vip(code: str) -> bool:
    if not code:
        return False
    code_hash = hashlib.sha256(code.encode("utf-8")).hexdigest()
    return code_hash == SECRET_CODE_HASH

def check_rate_limit(settings: dict) -> bool:
    """Verifica si el usuario puede transcribir."""
    if is_vip(settings.get("secret_code")):
        return True

    client_id = _get_client_ip()
    data = _load_tracker()
    
    now = time.time()
    user_data = data.get(client_id, {"runs": 0, "reset_at": now + 86400})
    
    # Reseteo diario
    if now > user_data["reset_at"]:
        user_data = {"runs": 0, "reset_at": now + 86400}
        
    if user_data["runs"] >= MAX_RUNS_PER_SESSION:
        return False
        
    return True

def increment_usage(settings: dict):
    """Suma 1 uso a la cuenta. No hace nada si es VIP."""
    if is_vip(settings.get("secret_code")):
        return
        
    client_id = _get_client_ip()
    data = _load_tracker()
    
    now = time.time()
    user_data = data.get(client_id, {"runs": 0, "reset_at": now + 86400})
    
    if now > user_data["reset_at"]:
        user_data = {"runs": 1, "reset_at": now + 86400}
    else:
        user_data["runs"] += 1
        
    data[client_id] = user_data
    _save_tracker(data)

def get_runs_for_user(settings: dict) -> tuple[int, int]:
    """Devuelve (usos_actuales, limite_maximo). Para VIP devuelve (0, 999)."""
    if is_vip(settings.get("secret_code")):
        return 0, 999
        
    client_id = _get_client_ip()
    data = _load_tracker()
    user_data = data.get(client_id, {"runs": 0})
    return user_data["runs"], MAX_RUNS_PER_SESSION
