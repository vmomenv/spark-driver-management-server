from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import crud, database

router = APIRouter()

@router.get("/api/pci_hardware/get", response_model=list)
async def get_pci_hardware(db: Session = Depends(database.get_db)):
    return crud.get_pci_hardware(db)

@router.get("/api/usb_hardware/get", response_model=list)
async def get_usb_hardware(db: Session = Depends(database.get_db)):
    return crud.get_usb_hardware(db)
