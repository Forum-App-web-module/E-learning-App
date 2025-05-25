from fastapi import HTTPException, status
from services.user_service import find_user_by_username


def admin_auth(payload):

    admin_status = find_user_by_username(payload["key"]["username"]).is_admin

    if not admin_status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Admin role authorization is needed.'
        )
    return True


