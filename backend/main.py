from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.trips import router as trips_router
from backend.api.tools import router as tools_router


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="TripGenie API",
    description="Agentic AI Travel Planning API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(trips_router)
app.include_router(tools_router)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "TripGenie API is running"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }