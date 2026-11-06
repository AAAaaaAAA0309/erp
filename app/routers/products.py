from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Product
from ..schemas import ProductCreate, ProductOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Product).all()

@router.post("", response_model=ProductOut)
def create_product(data: ProductCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = Product(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.delete("/{pid}")
def delete_product(pid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.get(Product, pid)
    if not p: raise HTTPException(404, "Не найден")
    db.delete(p); db.commit()
    return {"ok": True}