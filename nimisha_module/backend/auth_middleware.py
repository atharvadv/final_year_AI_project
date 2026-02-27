from fastapi import Header, HTTPException

from firebase_admin import auth

from database import admins, students


def verify_token(Authorization: str = Header(None)):

    if not Authorization:
        raise HTTPException(401, "Missing token")

    try:

        token = Authorization.split(" ")[1]

        decoded = auth.verify_id_token(token)

        return decoded

    except Exception:

        raise HTTPException(401, "Invalid or expired token")


def get_user_role(uid):

    if admins.find_one({"uid": uid}):

        return "admin"

    if students.find_one({"uid": uid}):

        return "student"

    return None


def require_admin(user):

    role = get_user_role(user["uid"])

    if role != "admin":

        raise HTTPException(403, "Admin access required")


def require_student(user):

    role = get_user_role(user["uid"])

    if role != "student":

        raise HTTPException(403, "Student access required")