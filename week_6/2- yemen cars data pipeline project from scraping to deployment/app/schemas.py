from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    name: str | None = None
    description: str | None = None
    model: int | None = None
    posted_at: datetime | None = None
    image_url: str | None = None
    price: float | None = None
    status: str | None = None
    mileage: int | None = None
    location: str | None = None
    country: str | None = None


class CarResponse(CarBase):
    id: int
    model_config = ConfigDict(from_attributes=True)