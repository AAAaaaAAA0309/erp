from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Partner
from ..schemas import PartnerCreate, PartnerOut
from ..auth import get_current_user

router = APIRouter(prefix="/api/partners", tags=["partners"])

@router.get("", response_model=list[PartnerOut])
def list_partners(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Partner).all()

@router.post("", response_model=PartnerOut)
def create_partner(data: PartnerCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = Partner(**data.model_dump())
    db.add(p); db.commit(); db.refresh(p)
    return p

@router.delete("/{pid}")
def delete_partner(pid: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    p = db.get(Partner, pid)
    if not p: raise HTTPException(404, "Не найден")
    db.delete(p); db.commit()
    return {"ok": True}