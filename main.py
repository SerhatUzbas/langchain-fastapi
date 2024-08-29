from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import database_rag, gitlab, gitlab_new, webbase_rag


# from routers import database_rag, pdf_summary

app = FastAPI()

origins = [
    "http://localhost:3000",  # React frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"hi": "item_id"}


# app.include_router(pdf_summary.router, prefix="/api/pdf-summary")
app.include_router(database_rag.router, prefix="/api/database-rag")
app.include_router(webbase_rag.router, prefix="/api/webbase-rag")
app.include_router(gitlab.router, prefix="/api/gitlab")
app.include_router(gitlab_new.router, prefix="/api/gitlab-new")
