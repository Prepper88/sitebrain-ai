import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from site_bot import SiteBot 
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse


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
    return StreamingResponse(site_bot.ask_question(query.question), media_type="text/plain")


@app.post("/stream-test")
async def stream_test():
    async def generator():
        for i in range(5):
            yield f"chunk {i}\n"
            await asyncio.sleep(1)
    return StreamingResponse(generator(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
