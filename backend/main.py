import json, secrets
from datetime import date
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from .auth import create_token, hash_password, token_user, verify_password
from .database import connection, init_db, trip_dict
from .planner import generate_trip

app=FastAPI(title="Roamly API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

class Credentials(BaseModel):
    email: str; password: str=Field(min_length=6); name: str|None=None
    @field_validator("email")
    @classmethod
    def valid_email(cls, value):
        value=value.strip().lower()
        if "@" not in value or "." not in value.split("@")[-1]: raise ValueError("Enter a valid email address")
        return value
class TripRequest(BaseModel):
    city:str=Field(min_length=2); start_date:date; days_count:int=Field(ge=1,le=7); budget:float=Field(gt=0); travelers:str="2 adults"; interests:list[str]=[]
class TripUpdate(BaseModel): itinerary:dict

@app.on_event("startup")
def startup(): init_db()
@app.get("/api/health")
def health(): return {"status":"ok"}
@app.post("/api/auth/register",status_code=201)
def register(data:Credentials):
    if not data.name: raise HTTPException(422,"Name is required")
    try:
        with connection() as db:
            cur=db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",(data.name.strip(),data.email.lower(),hash_password(data.password)))
            uid=cur.lastrowid
    except Exception as e:
        if "UNIQUE" in str(e): raise HTTPException(409,"An account with this email already exists")
        raise
    return {"token":create_token(uid),"user":{"id":uid,"name":data.name,"email":data.email.lower()}}
@app.post("/api/auth/login")
def login(data:Credentials):
    with connection() as db: row=db.execute("SELECT * FROM users WHERE email=?",(data.email.lower(),)).fetchone()
    if not row or not verify_password(data.password,row["password_hash"]): raise HTTPException(401,"Incorrect email or password")
    return {"token":create_token(row["id"]),"user":{"id":row["id"],"name":row["name"],"email":row["email"]}}
@app.post("/api/auth/guest")
def guest():
    email="guest@where-ujwal-wants-to-go.local"
    with connection() as db:
        row=db.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        if row: uid=row["id"]
        else:
            cur=db.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",("Ujwal",email,hash_password(secrets.token_urlsafe(16))))
            uid=cur.lastrowid
    return {"token":create_token(uid),"user":{"id":uid,"name":"Ujwal","email":email}}
@app.get("/api/me")
def me(user=Depends(token_user)): return user
@app.post("/api/trips",status_code=201)
def create_trip(data:TripRequest,user=Depends(token_user)):
    plan=generate_trip(data.city,data.start_date,data.days_count,data.budget,data.interests,data.travelers)
    with connection() as db:
        cur=db.execute("INSERT INTO trips(user_id,city,start_date,days_count,budget,travelers,interests,itinerary) VALUES(?,?,?,?,?,?,?,?)",(user["id"],data.city,str(data.start_date),data.days_count,data.budget,data.travelers,json.dumps(data.interests),json.dumps(plan,ensure_ascii=False)))
        row=db.execute("SELECT * FROM trips WHERE id=?",(cur.lastrowid,)).fetchone()
    return trip_dict(row)
@app.get("/api/trips")
def trips(user=Depends(token_user)):
    with connection() as db: rows=db.execute("SELECT * FROM trips WHERE user_id=? ORDER BY created_at DESC",(user["id"],)).fetchall()
    return [trip_dict(r) for r in rows]
@app.get("/api/trips/{trip_id}")
def get_trip(trip_id:int,user=Depends(token_user)):
    with connection() as db: row=db.execute("SELECT * FROM trips WHERE id=? AND user_id=?",(trip_id,user["id"])).fetchone()
    if not row: raise HTTPException(404,"Trip not found")
    return trip_dict(row)
@app.put("/api/trips/{trip_id}")
def update_trip(trip_id:int,data:TripUpdate,user=Depends(token_user)):
    with connection() as db:
        cur=db.execute("UPDATE trips SET itinerary=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",(json.dumps(data.itinerary,ensure_ascii=False),trip_id,user["id"]))
        if not cur.rowcount: raise HTTPException(404,"Trip not found")
        row=db.execute("SELECT * FROM trips WHERE id=?",(trip_id,)).fetchone()
    return trip_dict(row)
@app.delete("/api/trips/{trip_id}",status_code=204)
def delete_trip(trip_id:int,user=Depends(token_user)):
    with connection() as db:
        cur=db.execute("DELETE FROM trips WHERE id=? AND user_id=?",(trip_id,user["id"]))
        if not cur.rowcount: raise HTTPException(404,"Trip not found")
@app.post("/api/trips/{trip_id}/share")
def share(trip_id:int,user=Depends(token_user)):
    token=secrets.token_urlsafe(10)
    with connection() as db:
        cur=db.execute("UPDATE trips SET share_token=? WHERE id=? AND user_id=?",(token,trip_id,user["id"]))
        if not cur.rowcount: raise HTTPException(404,"Trip not found")
    return {"share_token":token,"path":f"/share/{token}"}
@app.get("/api/shared/{token}")
def shared(token:str):
    with connection() as db: row=db.execute("SELECT * FROM trips WHERE share_token=?",(token,)).fetchone()
    if not row: raise HTTPException(404,"Shared trip not found")
    return trip_dict(row)

# In production the Vite build is served by the same process as the API.
DIST=Path(__file__).resolve().parent.parent / "dist"
if DIST.exists():
    app.mount("/assets",StaticFiles(directory=DIST / "assets"),name="assets")
    @app.get("/{full_path:path}",include_in_schema=False)
    def frontend(full_path:str):
        candidate=(DIST / full_path).resolve()
        if candidate.is_file() and DIST.resolve() in candidate.parents: return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
