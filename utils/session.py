# utils/session.py


def get_user_details(session):
    """Extracts user ID, email, name, and avatar from Supabase session dict."""
    user_info = session.get("user", session)

    user_id = user_info.get("id", "unknown_id")
    user_email = user_info.get("email", "unknown")

    metadata = user_info.get("user_metadata", {})

    user_name = metadata.get("full_name") or metadata.get("name") or user_email

    avatar_url = metadata.get("avatar_url", "")

    return {"id": user_id, "email": user_email, "name": user_name, "avatar": avatar_url}
