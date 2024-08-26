import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.decider_agent import DeciderAgent
from repository.gitlab_agent import GitlabAgent
from repository.pdf_summary import PdfSummary
from repository.webbase_rag import WebLoaderRag


router = APIRouter(
    tags=["gitlab"],
)


@router.get("/")
async def get(request: Request, input: str):
    gitlab_agent = GitlabAgent()
    result = gitlab_agent.execute(question=input)
    return {"gitlab": result}


@router.get("/stream")
async def event_stream(request: Request, input: str):
    print("event stream")

    async def event_generator():
        gitlab_agent = GitlabAgent()
        async for chunk in gitlab_agent.stream(question=input):
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
