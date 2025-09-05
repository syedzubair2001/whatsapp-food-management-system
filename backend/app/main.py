from fastapi import FastAPI
from app import models, database
from app.routes import menu_routes, order_routes, auth

# Create DB tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="WhatsApp Food Ordering System")

# Register routers
app.include_router(menu_routes.router)
app.include_router(order_routes.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to WhatsApp Food Ordering System"}
