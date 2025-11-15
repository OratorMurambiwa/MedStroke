from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Patient
from typing import Optional
import uuid

router = APIRouter()

# -----------------------------
# SIMPLE IN-MEMORY SESSION STORE
# -----------------------------
active_sessions = {}


# -----------------------------
# DATABASE DEPENDENCY
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# SESSION HELPER
# -----------------------------
def get_current_user(request: Request) -> Optional[dict]:
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    return None


# -----------------------------
# REUSABLE HTML MESSAGE PAGE
# -----------------------------
def message_page(title: str, message: str, link_url: str, link_text: str):
    return HTMLResponse(f"""
        <html>
        <body style='background:black;color:white;text-align:center;padding-top:80px;'>
            <h2>{title}</h2>
            <p>{message}</p>
            <a href="{link_url}" style="color:#FDB927;">{link_text}</a>
        </body>
        </html>
    """)


# ============================================================
#                    PATIENT REGISTRATION
# ============================================================
@router.post("/register")
def register_patient(
    username: str = Form(...),
    password: str = Form(...),
    code: str = Form(...),
    db: Session = Depends(get_db)
):

    # Check if username exists
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return message_page(
            "Registration Failed",
            "Username already exists.",
            "/register-page",
            "Try Again"
        )

    # Create user
    user = User(username=username, password=password, role="Patient")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Try to link to existing patient record
    patient = db.query(Patient).filter_by(code=code).first()

    if patient:
        patient.linked_user_id = user.id
        db.commit()
        msg = "Your account is linked to an existing patient record."
    else:
        msg = "Account created. A technician will link your record later."

    return message_page(
        "Registration Successful",
        msg,
        "/login-page",
        "Go to Login"
    )


# ============================================================
#                STAFF REGISTRATION
# ============================================================
@router.post("/register-staff")
def register_staff(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):

    if role not in ["Technician", "Physician"]:
        return message_page(
            "Invalid Role",
            "Role must be Technician or Physician.",
            "/register-staff-page",
            "Try Again"
        )

    # Duplicate username check
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        return message_page(
            "Registration Failed",
            "Username already exists.",
            "/register-staff-page",
            "Try Again"
        )

    user = User(username=username, password=password, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)

    return message_page(
        "Registration Successful",
        f"{role} account created.",
        "/login-page",
        "Go to Login"
    )


# ============================================================
#                        LOGIN
# ============================================================
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):

    # Look up user with the correct role
    user = db.query(User).filter_by(username=username, role=role).first()

    if not user:
        return HTMLResponse("""
            <script>
            alert("User not found. Check username and role.");
            window.location.href = "/login-page";
            </script>
        """, status_code=401)

    if user.password != password:
        return HTMLResponse("""
            <script>
            alert("Incorrect password.");
            window.location.href = "/login-page";
            </script>
        """, status_code=401)

    # SESSION CREATION
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = {
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }

    # -----------------------------
    # REDIRECT BASED ON ROLE
    # -----------------------------
    if role == "Patient":
        patient = db.query(Patient).filter_by(linked_user_id=user.id).first()

        if not patient:
            return HTMLResponse("""
                <script>
                alert("No patient record linked yet.");
                window.location.href = "/login-page";
                </script>
            """, status_code=404)

        redirect_url = f"/patient-view?code={patient.code}"

    elif role == "Technician":
        redirect_url = "/technician-dashboard"

    elif role == "Physician":
        redirect_url = "/physician-dashboard"

    else:
        raise HTTPException(status_code=400, detail="Invalid role.")

    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie("session_id", session_id, httponly=True, max_age=3600)

    return response


# ============================================================
#                GET CURRENT USER SESSION
# ============================================================
@router.get("/current-user")
def get_current_user_info(request: Request):
    user_info = get_current_user(request)
    if not user_info:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_info


# ============================================================
#                        LOGOUT
# ============================================================
@router.post("/logout")
def logout(request: Request):
    session_id = request.cookies.get("session_id")

    if session_id and session_id in active_sessions:
        del active_sessions[session_id]

    response = RedirectResponse(url="/login-page", status_code=302)
    response.delete_cookie("session_id")
    return response
