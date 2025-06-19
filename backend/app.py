from starlette.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
# Initialize FastAPI
app = FastAPI(
    title="AI Emoji Suggester",
    description="Get relevant emojis for your text using NLP",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins='*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

