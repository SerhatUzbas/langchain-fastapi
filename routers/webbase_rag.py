import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.decider_agent import DeciderAgent
from repository.pdf_summary import PdfSummary
from repository.webbase_rag import WebLoaderRag


router = APIRouter(
    tags=["webbase_rag"],
)

SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]


@router.get("/")
async def get():
    summary = await PdfSummary.create_post()
    return {"pdf_summary": summary}


@router.get("/stream")
async def event_stream(request: Request, input: str):

    async def event_generator():
        decideragent = DeciderAgent(SQLALCHEMY_DATABASE_URL)

        async for chunk in decideragent.answer_stream(question=input):
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
