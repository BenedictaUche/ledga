from fastapi import APIRouter, HTTPException
from supabase import create_client
from datetime import date, datetime
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

router = APIRouter(prefix="/shops", tags=["shops"])
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

@router.get("/debug/uipath")
async def debug_uipath():
    from services.uipath import get_access_token, get_release_key
    token = await get_access_token()
    releases = await get_release_key("Ledga") if token else None
    return {
        "token_obtained": token is not None,
        "token_preview": token[:20] + "..." if token else None,
        "release_key": releases
    }
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


@router.post("/{shop_id}/close-day")
async def close_business_day(shop_id: str):
    """Operator manually closes the business day for a shop."""
    today = date.today().isoformat()

    # Get today's business day
    day = supabase.table("business_days") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .eq("date", today) \
        .execute()

    if not day.data:
        raise HTTPException(status_code=404, detail="No active business day found")

    business_day = day.data[0]

    # Get shop info for summary
    shop = supabase.table("shops") \
        .select("*") \
        .eq("id", shop_id) \
        .execute()

    shop_data = shop.data[0] if shop.data else {}

    # Get outstanding credit
    customers = supabase.table("customers") \
        .select("name, total_credit_owed") \
        .eq("shop_id", shop_id) \
        .gt("total_credit_owed", 0) \
        .execute()

    # Build summary
    summary = {
        "shop_name": shop_data.get("name"),
        "owner_name": shop_data.get("owner_name"),
        "date": today,
        "total_sales": business_day["total_sales"],
        "total_profit": business_day["total_profit"],
        "total_credit_given": business_day["total_credit_given"],
        "outstanding_credit": [
            {"customer": c["name"], "amount": c["total_credit_owed"]}
            for c in (customers.data or [])
        ]
    }

    # Close the business day
    supabase.table("business_days").update({
        "status": "closed",
        "closed_at": datetime.utcnow().isoformat(),
        "summary_sent": True
    }).eq("id", business_day["id"]).execute()

    print(f"[EOD] Day closed for {shop_data.get('name')}. Summary: {summary}")

    return {
        "status": "closed",
        "summary": summary
    }
