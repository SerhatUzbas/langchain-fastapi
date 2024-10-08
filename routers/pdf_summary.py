from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.pdf_summary import PdfSummary


router = APIRouter(
    tags=["pdf_summary"],
)


@router.get("/")
async def get():
    summary = await PdfSummary.create_post()
    return {"pdf_summary": summary}


@router.get("/stream")
async def event_stream(request: Request, input: str):

    async def event_generator():
        async for chunk in PdfSummary.create_post_stream(input=input):
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
