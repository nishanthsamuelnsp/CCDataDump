from core.config import ADMIN_EMAILS, DEV_MODE, DEV_USER_EMAIL

def get_current_user():
    if DEV_MODE:
        return {"email": DEV_USER_EMAIL, "name": "Dev User"}
    return {"email": None, "name": "Guest"}

def get_user_role(user):
    email = (user or {}).get("email")
    return "admin" if email in ADMIN_EMAILS else "public"
