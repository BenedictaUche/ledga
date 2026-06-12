from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import transactions, shops, exceptions

app = FastAPI(
    title="Ledga API",
    description="BaaS back-office agent for informal African SMBs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(shops.router)
app.include_router(exceptions.router)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "Ledga API"}
