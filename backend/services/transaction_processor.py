from datetime import date
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from services.parser import parse_transaction
from services.uipath import start_business_day_process, create_action_center_task
import asyncio
from concurrent.futures import ThreadPoolExecutor

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_or_create_business_day(shop_id: str) -> dict:
    """Get today's business day for a shop, or create one if it doesn't exist."""
    today = date.today().isoformat()
    result = supabase.table("business_days") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .eq("date", today) \
        .execute()

    if result.data:
        return result.data[0]

    new_day = supabase.table("business_days") \
        .insert({"shop_id": shop_id, "date": today, "status": "open"}) \
        .execute()
    shop = supabase.table("shops").select("name").eq("id", shop_id).execute()
    shop_name = shop.data[0]["name"] if shop.data else "Unknown Shop"
    with ThreadPoolExecutor() as pool:
        pool.submit(asyncio.run, start_business_day_process(shop_id, shop_name, new_day.data[0]["id"]))
    return new_day.data[0]



def get_or_create_product(shop_id: str, product_name: str) -> dict:
    """Find a product by name, or auto-create it if it doesn't exist."""
    name_lower = product_name.lower().strip()

    # Try exact match first (case-insensitive)
    result = supabase.table("products") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .ilike("name", name_lower) \
        .execute()

    if result.data:
        return result.data[0]

    # Auto-create the product
    new_product = supabase.table("products").insert({
        "shop_id": shop_id,
        "name": product_name.strip().title(),
        "is_auto_created": True
    }).execute()

    # Auto-create inventory entry at 0
    supabase.table("inventory").insert({
        "shop_id": shop_id,
        "product_id": new_product.data[0]["id"],
        "quantity": 0
    }).execute()

    return new_product.data[0]

def get_or_create_customer(shop_id: str, customer_name: str) -> dict:
    """Find a customer by name, or create them if they don't exist."""
    result = supabase.table("customers") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .ilike("name", customer_name.strip()) \
        .execute()

    if result.data:
        return result.data[0]

    new_customer = supabase.table("customers").insert({
        "shop_id": shop_id,
        "name": customer_name.strip().title()
    }).execute()
    return new_customer.data[0]

def update_inventory(shop_id: str, product_id: str, quantity_delta: int) -> dict:
    """Update inventory and return new quantity."""
    result = supabase.table("inventory") \
        .select("*") \
        .eq("shop_id", shop_id) \
        .eq("product_id", product_id) \
        .execute()

    if not result.data:
        supabase.table("inventory").insert({
            "shop_id": shop_id,
            "product_id": product_id,
            "quantity": max(0, quantity_delta)
        }).execute()
        return {"quantity": max(0, quantity_delta)}

    row = result.data[0]
    new_qty = max(0, row["quantity"] + quantity_delta)
    updated = supabase.table("inventory") \
        .update({"quantity": new_qty}) \
        .eq("id", row["id"]) \
        .execute()
    return updated.data[0]

def check_and_create_exceptions(
    shop_id: str,
    business_day_id: str,
    transaction_id: str,
    product: dict,
    new_inventory_qty: int,
    transaction_amount: float,
    is_credit: bool,
    customer_id: str = None
):
    """Check for exception conditions and create exception records."""
    exceptions = []

    # Low stock check
    threshold = product.get("low_stock_threshold", 10)
    if new_inventory_qty <= threshold:
        exceptions.append({
            "shop_id": shop_id,
            "business_day_id": business_day_id,
            "transaction_id": transaction_id,
            "exception_type": "low_stock",
            "severity": "high" if new_inventory_qty == 0 else "medium",
            "description": f"{product['name']} is low: {new_inventory_qty} {product.get('unit','units')} remaining",
            "status": "pending"
        })

    # Large credit check (over ₦10,000 in a single transaction)
    if is_credit and transaction_amount > 10000:
        exceptions.append({
            "shop_id": shop_id,
            "business_day_id": business_day_id,
            "transaction_id": transaction_id,
            "exception_type": "large_credit",
            "severity": "high",
            "description": f"Large credit of ₦{transaction_amount:,.2f} given",
            "status": "pending"
        })

    # Overdue credit check
    if customer_id:
        overdue = supabase.rpc("check_overdue_credit", {
            "p_customer_id": customer_id,
            "p_days": 7
        }).execute()
        if overdue.data:
            exceptions.append({
                "shop_id": shop_id,
                "business_day_id": business_day_id,
                "exception_type": "overdue_credit",
                "severity": "medium",
                "description": f"Customer has credit overdue by more than 7 days",
                "status": "pending"
            })

    for exc in exceptions:
        result = supabase.table("exceptions").insert(exc).execute()
        exc_id = result.data[0]["id"]
        # Notify UiPath Action Center
        with ThreadPoolExecutor() as pool:
            pool.submit(asyncio.run, create_action_center_task(
                shop_name=product.get("name", "Unknown Shop"),
                exception_type=exc["exception_type"],
                description=exc["description"],
                exception_id=exc_id
            ))

    return exceptions

def update_business_day_totals(business_day_id: str, profit: float, sales: float, credit: float):
    """Increment the running totals on the business day."""
    current = supabase.table("business_days") \
        .select("total_sales, total_profit, total_credit_given") \
        .eq("id", business_day_id) \
        .execute()

    if current.data:
        row = current.data[0]
        supabase.table("business_days").update({
            "total_sales": row["total_sales"] + sales,
            "total_profit": row["total_profit"] + profit,
            "total_credit_given": row["total_credit_given"] + credit,
        }).eq("id", business_day_id).execute()

def process_message(shop_id: str, raw_message: str) -> dict:
    """
    Main entry point. Takes a shop ID and raw owner message.
    Returns a summary of what was processed and any exceptions raised.
    """
    # Step 1: Parse the message
    parsed = parse_transaction(raw_message)

    # Step 2: If parsing failed entirely, create an exception and return early
    if parsed["parse_status"] == "failed":
        business_day = get_or_create_business_day(shop_id)
        supabase.table("exceptions").insert({
            "shop_id": shop_id,
            "business_day_id": business_day["id"],
            "exception_type": "parse_failed",
            "severity": "medium",
            "description": f"Could not parse message: '{raw_message[:100]}'. Reason: {parsed.get('ambiguity_reason', 'Unknown')}",
            "status": "pending"
        }).execute()
        return {
            "status": "failed",
            "message": "Could not parse your message. Your operator has been notified.",
            "exceptions_raised": 1
        }

    # Step 3: Get or create today's business day
    business_day = get_or_create_business_day(shop_id)
    business_day_id = business_day["id"]

    results = []
    total_exceptions = 0

    # Step 4: Process each transaction in the message
    for t in parsed["transactions"]:
        product = get_or_create_product(shop_id, t["product_name"])
        product_id = product["id"]

        # Resolve customer if credit
        customer_id = None
        if t.get("is_credit") and t.get("customer_name"):
            customer = get_or_create_customer(shop_id, t["customer_name"])
            customer_id = customer["id"]

        # Calculate amounts
        qty = t.get("quantity", 1)
        unit_price = t.get("unit_price") or product.get("selling_price", 0)
        cost_price = product.get("cost_price", 0)
        total_amount = qty * unit_price
        profit = qty * (unit_price - cost_price)

        # Determine inventory delta
        if t["transaction_type"] == "restock":
            inventory_delta = qty
            profit = 0
        else:
            inventory_delta = -qty

        # Write transaction record
        tx = supabase.table("transactions").insert({
            "shop_id": shop_id,
            "business_day_id": business_day_id,
            "product_id": product_id,
            "customer_id": customer_id,
            "raw_message": raw_message,
            "transaction_type": t["transaction_type"],
            "quantity": qty,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "cost_at_time": cost_price,
            "profit": profit,
            "is_credit": t.get("is_credit", False),
            "parse_status": parsed["parse_status"]
        }).execute()

        transaction_id = tx.data[0]["id"]

        # Update inventory
        new_inventory = update_inventory(shop_id, product_id, inventory_delta)

        # Handle credit ledger
        if t.get("is_credit") and customer_id:
            customer = supabase.table("customers") \
                .select("total_credit_owed") \
                .eq("id", customer_id) \
                .execute()

            current_owed = customer.data[0]["total_credit_owed"] if customer.data else 0
            new_balance = current_owed + total_amount

            supabase.table("credit_ledger").insert({
                "shop_id": shop_id,
                "customer_id": customer_id,
                "transaction_id": transaction_id,
                "entry_type": "credit_given",
                "amount": total_amount,
                "balance_after": new_balance
            }).execute()

            supabase.table("customers") \
                .update({"total_credit_owed": new_balance}) \
                .eq("id", customer_id).execute()

        # Check for exceptions
        exceptions = check_and_create_exceptions(
            shop_id, business_day_id, transaction_id,
            product, new_inventory["quantity"],
            total_amount, t.get("is_credit", False), customer_id
        )
        total_exceptions += len(exceptions)

        # Update business day running totals
        update_business_day_totals(
            business_day_id,
            profit=profit,
            sales=total_amount if not t.get("is_credit") else 0,
            credit=total_amount if t.get("is_credit") else 0
        )

        results.append({
            "product": product["name"],
            "quantity": qty,
            "amount": total_amount,
            "profit": profit,
            "type": t["transaction_type"]
        })

    return {
        "status": parsed["parse_status"],
        "transactions_recorded": len(results),
        "exceptions_raised": total_exceptions,
        "results": results,
        "ambiguity_reason": parsed.get("ambiguity_reason")
    }
