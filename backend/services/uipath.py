import httpx
from config import UIPATH_BASE_URL, UIPATH_ACCOUNT, UIPATH_TENANT, UIPATH_TOKEN

BASE = f"{UIPATH_BASE_URL}/{UIPATH_ACCOUNT}/{UIPATH_TENANT}"

HEADERS = {
    "Authorization": f"Bearer {UIPATH_TOKEN}",
    "Content-Type": "application/json",
    "X-UIPATH-TenantName": UIPATH_TENANT
}

def get_headers():
    return HEADERS

async def start_business_day_process(shop_id: str, shop_name: str, business_day_id: str) -> dict:
    """
    Triggers the Ledga Business Day BPMN process in UiPath Maestro
    for a specific shop when their business day opens.
    """
    url = f"{BASE}/maestro_/api/v1/processes/start"
    payload = {
        "processName": "LedgaBusinessDay",
        "inputArguments": {
            "shopId": shop_id,
            "shopName": shop_name,
            "businessDayId": business_day_id,
            "endOfDay": False,
            "exceptionsRaised": 0,
            "parseStatus": "pending"
        }
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload, headers=get_headers())
            if response.status_code in (200, 201, 202):
                data = response.json()
                print(f"[UIPATH] Process started for {shop_name}: {data}")
                return {"success": True, "data": data}
            else:
                print(f"[UIPATH] Failed to start process: {response.status_code} {response.text}")
                return {"success": False, "error": response.text}
    except Exception as e:
        print(f"[UIPATH] Exception starting process: {e}")
        return {"success": False, "error": str(e)}

async def create_action_center_task(
    shop_name: str,
    exception_type: str,
    description: str,
    exception_id: str
) -> dict:
    """
    Creates a human task in UiPath Action Center when an exception is detected.
    Operator sees this task and can resolve or dismiss it.
    """
    url = f"{BASE}/orchestrator_/odata/Tasks/UiPath.Server.Configuration.OData.CreateTask"
    payload = {
        "Title": f"[{shop_name}] {exception_type.replace('_', ' ').title()}",
        "Type": "ExternalTask",
        "Priority": "High",
        "CatalogName": "LedgaExceptions",
        "Data": {
            "shopName": shop_name,
            "exceptionType": exception_type,
            "description": description,
            "exceptionId": exception_id
        }
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload, headers=get_headers())
            if response.status_code in (200, 201, 202):
                data = response.json()
                print(f"[UIPATH] Action Center task created: {data}")
                return {"success": True, "task_id": data.get("Id")}
            else:
                print(f"[UIPATH] Failed to create task: {response.status_code} {response.text}")
                return {"success": False, "error": response.text}
    except Exception as e:
        print(f"[UIPATH] Exception creating task: {e}")
        return {"success": False, "error": str(e)}

async def complete_business_day(business_day_id: str, shop_name: str) -> dict:
    """
    Signals UiPath that the business day is complete.
    Triggers the end-of-day branch in the BPMN process.
    """
    url = f"{BASE}/maestro_/api/v1/processes/signal"
    payload = {
        "processName": "LedgaBusinessDay",
        "signal": "EndOfDay",
        "correlationId": business_day_id,
        "inputArguments": {
            "endOfDay": True,
            "shopName": shop_name
        }
    }
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload, headers=get_headers())
            if response.status_code in (200, 201, 202):
                print(f"[UIPATH] End of day signalled for {shop_name}")
                return {"success": True}
            else:
                print(f"[UIPATH] Failed to signal end of day: {response.status_code} {response.text}")
                return {"success": False, "error": response.text}
    except Exception as e:
        print(f"[UIPATH] Exception signalling end of day: {e}")
        return {"success": False, "error": str(e)}
