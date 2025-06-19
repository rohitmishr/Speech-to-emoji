from backend.app import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.emoji:app", host="localhost", port=8000, reload=True)