from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pdf_summary

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


app.include_router(pdf_summary.router, prefix="/api/pdf-summary")
