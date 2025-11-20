import asyncio
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from site_bot import SiteBot 
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from file_management import router as file_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create an instance of SiteBot (custom class that handles document QA)
    site_bot = SiteBot()
    # Load local documents from the 'docs/' directory into the SiteBot
    site_bot.load_documents("docs/")
    # Attach the SiteBot instance to the FastAPI app state (shared across requests)
    app.state.site_bot = site_bot
    print("Documents loaded, app starting...")

    yield

    print("🧹 Shutting down...")

# Initialize FastAPI app with the lifespan handler
app = FastAPI(lifespan=lifespan)

app.include_router(file_router, prefix="/files", tags=["File Service"])

class Query(BaseModel):
    question: str

#  Main API endpoint — ask a question to the SiteBot
@app.post("/ask")
async def ask(query: Query):
    site_bot = app.state.site_bot
    return StreamingResponse(site_bot.ask_question(query.question), media_type="text/plain")

#  Test endpoint — simulate streaming chunks for debugging
@app.post("/stream-test")
async def stream_test():
    async def generator():
        for i in range(5):
            yield f"chunk {i}\n"
            await asyncio.sleep(1)
    return StreamingResponse(generator(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
