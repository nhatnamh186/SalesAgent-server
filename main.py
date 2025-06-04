from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from apis import utils, MapFactory, LinkedinFactory

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(utils.router)
app.include_router(MapFactory.router)
app.include_router(LinkedinFactory.router)

@app.get("/")
async def root():
    return {"message": "✅ Server is running!"}
