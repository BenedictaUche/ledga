from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.transaction_processor import process_message

router = APIRouter(prefix="/transactions", tags=["transactions"])

class MessageInput(BaseModel):
    shop_id: str
    message: str

@router.post("/message")
async def record_message(payload: MessageInput):
    """
    Receive a raw message from a shop owner and process it.
    This is the main endpoint the operator dashboard calls.
    """
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    result = process_message(payload.shop_id, payload.message)
    return result
