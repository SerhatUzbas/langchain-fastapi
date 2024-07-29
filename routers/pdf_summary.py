from fastapi import APIRouter
from repository import pdf_summary


router = APIRouter(
    tags=["pdf_summary"],
)


@router.get("/")
def get():
    summary = pdf_summary.PdfSummary.create_post()
    return {"pdf_summary": summary}
