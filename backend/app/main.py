from fastapi import FastAPI

from app.api.v1.api import router

app = FastAPI(
    title="Bill Splitter",
    description="A small utility to split bills amongst friends",
)
app.include_router(router, prefix="/api/v1")
