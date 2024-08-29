import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.decider_agent import DeciderAgent
from repository.gitlab_agent import GitlabAgent
from repository.pdf_summary import PdfSummary
from repository.webbase_rag import WebLoaderRag
from tools.gitlab_tools import GitlabTools


router = APIRouter(
    tags=["gitlab-new"],
)


@router.get("/")
async def get(request: Request):
    GitlabTool = GitlabTools()
    result = GitlabTool.print_repo_tree()
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
