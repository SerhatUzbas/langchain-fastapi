from fastapi import FastAPI

from routers import pdf_summary

app = FastAPI()


@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"hi": "item_id"}


app.include_router(pdf_summary.router, prefix="/api/pdf-summary")
