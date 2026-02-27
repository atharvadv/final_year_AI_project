import os

from fastapi import FastAPI, Depends, UploadFile, File

from auth_middleware import verify_token, require_admin

from database import admins, students, files

import firebase_admin_init


UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


app = FastAPI()


# =====================================
# ADMIN REGISTRATION
# =====================================

@app.post("/admin/register")
def register_admin(user=Depends(verify_token)):

    uid = user["uid"]

    email = user["email"]

    if admins.find_one({"uid": uid}):

        return {"message": "Already registered"}

    admins.insert_one({

        "uid": uid,

        "email": email,

        "role": "admin"

    })

    return {"message": "Admin registered"}
    

# =====================================
# STUDENT REGISTRATION
# =====================================

@app.post("/student/register")
def register_student(user=Depends(verify_token)):

    uid = user["uid"]

    email = user["email"]

    if students.find_one({"uid": uid}):

        return {"message": "Already registered"}

    students.insert_one({

        "uid": uid,

        "email": email,

        "role": "student"

    })

    return {"message": "Student registered"}


# =====================================
# ROLE CHECK
# =====================================

@app.get("/my-role")
def get_role(user=Depends(verify_token)):

    uid = user["uid"]

    if admins.find_one({"uid": uid}):

        return {"role": "admin"}

    if students.find_one({"uid": uid}):

        return {"role": "student"}

    return {"role": "none"}


# =====================================
# ADMIN FILE UPLOAD (SECURE)
# =====================================

@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user=Depends(verify_token)
):

    require_admin(user)

    uid = user["uid"]

    filepath = os.path.join(
        UPLOAD_FOLDER,
        file.filename
    )

    with open(filepath, "wb") as f:

        f.write(file.file.read())


    files.insert_one({

        "filename": file.filename,

        "owner_uid": uid,

        "uploaded_by": "admin"

    })

    return {"message": "File uploaded"}


# =====================================
# STUDENT FILE ACCESS (DATA ISOLATION)
# =====================================

@app.get("/my-files")
def get_my_files(user=Depends(verify_token)):

    uid = user["uid"]

    result = []

    for f in files.find(
        {"owner_uid": uid},
        {"_id": 0}
    ):

        result.append(f)

    return result


# =====================================
# SECURE FILE ACCESS BY NAME
# =====================================

@app.get("/file/{filename}")
def access_file(
    filename: str,
    user=Depends(verify_token)
):

    uid = user["uid"]

    file_record = files.find_one({

        "filename": filename,

        "owner_uid": uid

    })

    if not file_record:

        return {"error": "Unauthorized"}

    return {

        "filename": filename,

        "status": "Authorized"

    }