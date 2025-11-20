import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import create_document

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
    source: Optional[str] = "portfolio"


@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}


@app.post("/contact")
async def contact(message: ContactMessage):
    try:
        # Persist message to database (collection name inferred: "contactmessage" -> use explicit)
        doc = message.model_dump()
        await create_document("contact", doc)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_database():
    """Quick connectivity check"""
    info = {"backend": "running"}
    try:
        # Try writing a tiny heartbeat doc (won't fail if DB not configured; helper handles it)
        await create_document("heartbeat", {"ok": True})
        info["database"] = "ok"
    except Exception as e:
        info["database"] = f"error: {str(e)[:120]}"
    return info


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
