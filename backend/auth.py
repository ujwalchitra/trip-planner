import base64, hashlib, hmac, json, os, secrets, time
from fastapi import Depends, Header, HTTPException
from .database import connection

SECRET = os.getenv("ROAMLY_SECRET", "roamly-local-development-secret")

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 180_000)
    return base64.urlsafe_b64encode(salt + digest).decode()

def verify_password(password: str, stored: str) -> bool:
    raw = base64.urlsafe_b64decode(stored.encode())
    return hmac.compare_digest(raw[16:], hashlib.pbkdf2_hmac("sha256", password.encode(), raw[:16], 180_000))

def create_token(user_id: int) -> str:
    body = base64.urlsafe_b64encode(json.dumps({"sub": user_id, "exp": int(time.time()) + 604800}).encode()).decode().rstrip("=")
    sig = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    return f"{body}.{sig}"

def token_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in required")
    try:
        body, sig = authorization[7:].split(".")
        expected = hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected): raise ValueError()
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if payload["exp"] < time.time(): raise ValueError()
        with connection() as db: user = db.execute("SELECT id,name,email FROM users WHERE id=?", (payload["sub"],)).fetchone()
        if not user: raise ValueError()
        return dict(user)
    except Exception:
        raise HTTPException(401, "Invalid or expired session")
