from fastapi import APIRouter, HTTPException
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

router = APIRouter(prefix="/shops", tags=["shops"])
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@router.get("/{operator_id}")
async def get_shops(operator_id: str):
    """Get all shops for an operator."""
    result = supabase.table("shops") \
        .select("*, business_days(*)") \
        .eq("operator_id", operator_id) \
        .eq("is_active", True) \
        .execute()
    return result.data

@router.get("/{shop_id}/summary")
async def get_today_summary(shop_id: str):
    """Get today's business summary for a shop."""
    from datetime import date
    today = date.today().isoformat()

    day = supabase.table("business_days") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .eq("date", today) \
        .execute()

    if not day.data:
        return {"message": "No activity today yet"}

    exceptions = supabase.table("exceptions") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .eq("status", "pending") \
        .execute()

    return {
        "business_day": day.data[0],
        "pending_exceptions": exceptions.data
    }
