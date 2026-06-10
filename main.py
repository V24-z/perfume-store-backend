from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.banner_route import router as banner_router
from routes.product_route import router as product_router
from routes.category_route import router as category_router
from fastapi.middleware.cors import CORSMiddleware
from routes.cart_route import router as cart_router



app = FastAPI()
origins = [
    "https://perfume-store-frontend-theta.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # allow these origins
    allow_credentials=True,
    allow_methods=["*"],     # GET, POST, PUT, DELETE, etc
    allow_headers=["*"],     # allow headers like Authorization
)
app.include_router(auth_router)
app.include_router(banner_router)
app.include_router(product_router)
app.include_router(category_router)
app.include_router(cart_router)