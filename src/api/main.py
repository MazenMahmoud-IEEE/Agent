from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.context_judge_api import router as context_router
from src.api.web_search_api import router as web_router

app = FastAPI(title="Agent - API (Week1)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(context_router, prefix="/api")
app.include_router(web_router, prefix="/api")


@app.get("/")
async def root():
    return {"status": "ok", "message": "Agent API (Week1). Use /api/presence_judge and /api/web_search"}
