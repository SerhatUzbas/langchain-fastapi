from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.pdf_summary import PdfSummary
from repository.webbase_rag import WebLoaderRag


router = APIRouter(
    tags=["webbase_rag"],
)


@router.get("/")
async def get():
    summary = await PdfSummary.create_post()
    return {"pdf_summary": summary}


@router.get("/stream")
async def event_stream(request: Request):
    async def event_generator():
        async for chunk in WebLoaderRag.answer_stream(
            input="I need an address of library"
        ):
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
