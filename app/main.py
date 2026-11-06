from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import User
from .auth import verify_password, create_token, get_current_user
from .routers import products, partners, warehouses, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI ERP MVP")
templates = Jinja2Templates(directory="templates")

app.include_router(products.router)
app.include_router(partners.router)
app.include_router(warehouses.router)
app.include_router(chat.router)

@app.post("/api/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Неверные логин или пароль")
    return {"access_token": create_token(user.username), "token_type": "bearer", "role": user.role}

@app.get("/", response_class=HTMLResponse)
def home():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
def app_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})