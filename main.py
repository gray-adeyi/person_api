from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from db import initialize_database
from routers import person_router

app = FastAPI(
    title="Person API",
    description="A simple REST API capable of CRUD operations on a `Person` resource",
    contact={"email": "adeyigbenga005@gmail.com"},
)
app.include_router(person_router)


@app.on_event("startup")
async def init():
    await initialize_database()


@app.get("/")
def redirect_to_docs():
    return RedirectResponse("/docs")
