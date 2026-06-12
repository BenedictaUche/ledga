import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
UIPATH_BASE_URL = os.getenv("UIPATH_BASE_URL")
UIPATH_ACCOUNT = os.getenv("UIPATH_ACCOUNT")
UIPATH_TENANT = os.getenv("UIPATH_TENANT")
UIPATH_TOKEN = os.getenv("UIPATH_TOKEN")
