from fastapi import APIRouter
from pydantic import BaseModel
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

router = APIRouter(prefix="/exceptions", tags=["exceptions"])
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class ResolveInput(BaseModel):
    operator_id: str
    status: str  # "resolved" | "dismissed" | "acknowledged"

@router.get("/operator/{operator_id}")
async def get_operator_exceptions(operator_id: str):
    """Get all pending exceptions across all shops for an operator."""
    shops = supabase.table("shops") \
        .select("id") \
        .eq("operator_id", operator_id) \
        .execute()

    shop_ids = [s["id"] for s in shops.data]
    if not shop_ids:
        return []

    result = supabase.table("exceptions") \
        .select("*, shops(name, owner_name)") \
        .in_("shop_id", shop_ids) \
        .eq("status", "pending") \
        .order("created_at", desc=True) \
        .execute()

    return result.data

@router.patch("/{exception_id}/resolve")
async def resolve_exception(exception_id: str, payload: ResolveInput):
    """Operator resolves or dismisses an exception."""
    from datetime import datetime
    result = supabase.table("exceptions").update({
        "status": payload.status,
        "resolved_by": payload.operator_id,
        "resolved_at": datetime.utcnow().isoformat()
    }).eq("id", exception_id).execute()
    return result.data[0]
