from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from repository import pdf_summary


router = APIRouter(
    tags=["pdf_summary"],
)


@router.get("/")
async def get():
    summary = await pdf_summary.PdfSummary.create_post()
    return {"pdf_summary": summary}


@router.get("/stream")
async def event_stream(request: Request):
    async def event_generator():
        async for chunk in pdf_summary.PdfSummary.create_post_stream():
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
