from fastapi import FastAPI
from app.core.middleware import setup_middleware
from app.database import engine, Base
from app.routes import auth
from app.models import user
from app.routes import test


app = FastAPI(
    title="Smart Food Stall Backend",
    version="1.0.0"
)

setup_middleware(app)
# app = FastAPI()

# @app.on_event("startup")
# def on_startup():
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

app.include_router(test.router)


from app.routes import menu
from app.models import menu as menu_model 

app.include_router(menu.router)



from app.routes import order
from app.models import order as order_model

app.include_router(order.router)


@app.get("/")
def health_check():
    return {"status": "Backend running successfully"}
