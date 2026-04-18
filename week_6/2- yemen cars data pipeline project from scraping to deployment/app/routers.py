from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Car
from app.schemas import CarResponse

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("/", response_model=list[CarResponse])
def get_all_cars(db: Session = Depends(get_db)):
    return db.query(Car).all()


@router.get("/{car_id}", response_model=CarResponse)
def get_car_by_id(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car
