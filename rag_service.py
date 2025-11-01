from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from site_bot import SiteBot 
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    site_bot = SiteBot()
    site_bot.load_documents("docs/")
    app.state.site_bot = site_bot
    print("✅ Documents loaded, app starting...")

    yield

    print("🧹 Shutting down...")

app = FastAPI(lifespan=lifespan)

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask(query: Query):
    site_bot = app.state.site_bot
    return site_bot.ask_question(query.question)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
