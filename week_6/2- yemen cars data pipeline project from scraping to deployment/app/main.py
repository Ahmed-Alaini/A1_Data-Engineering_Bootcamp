from fastapi import FastAPI

from app.db import Base, engine
from app.routers import router as cars_router

app = FastAPI(title="Cars API")

Base.metadata.create_all(bind=engine)
app.include_router(cars_router)


@app.get("/")
def root():
    return {"message": "Cars API is running"}
