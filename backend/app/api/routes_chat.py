from fastapi import APIRouter
from backend.app.schemas.chat import ChatQueryRequest, ChatQueryResponse
from backend.app.llm.explanation import GroundedExplanationLayer

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("/query", response_model=ChatQueryResponse)
async def query_vehicle_gpt(request: ChatQueryRequest):
    """
    Primary Natural Language Query Endpoint.
    Interprets queries, triggers verified read-only analytics, and returns grounded answers.
    """
    response = GroundedExplanationLayer.process_query(
        query=request.query,
        vehicle_id=request.vehicle_id
    )
    return response
