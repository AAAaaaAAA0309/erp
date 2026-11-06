from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Warehouse
from ..schemas import WarehouseCreate, WarehouseOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])

@router.get("", response_model=list[WarehouseOut])
def list_warehouses(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Warehouse).all()

@router.post("", response_model=WarehouseOut)
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    w = Warehouse(**data.model_dump())
    db.add(w); db.commit(); db.refresh(w)
    return w

@router.delete("/{wid}")
def delete_warehouse(wid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    w = db.get(Warehouse, wid)
    if not w: raise HTTPException(404, "Не найден")
    db.delete(w); db.commit()
    return {"ok": True}