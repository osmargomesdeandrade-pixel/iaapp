from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello from {{ project_name }}"}


# Run with: uvicorn main:app --reload --port 8000
