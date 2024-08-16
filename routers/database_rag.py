import os
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from repository.database_rag import (
    DatabaseAgentRag,
    DatabaseChainRag,
    SQLDatabaseAgent,
)
from repository.pdf_summary import PdfSummary


router = APIRouter(
    tags=["database-rag"],
)

SQLALCHEMY_DATABASE_URL = os.environ["SQLALCHEMY_DATABASE_URL"]


@router.get("/")
async def get():
    # result = await DatabaseRag.execute()
    # result = DBMONSTER.execute()
    # result = DatabaseAgentRag.execute()
    agent = SQLDatabaseAgent(SQLALCHEMY_DATABASE_URL)
    result = agent.execute(question="How many users in database?")
    return {"pdf_summary": result}


@router.get("/stream")
async def event_stream(request: Request, input: str):

    async def event_generator():
        async for chunk in PdfSummary.create_post_stream(input=input):
            if await request.is_disconnected():
                break
            yield f"data: {chunk}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
