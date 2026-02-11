from supabase import create_client

url = "https://SEU_URL.supabase.co"
key = "SUA_SERVICE_ROLE"

supabase = create_client(url, key)

print("OK")
