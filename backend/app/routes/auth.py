from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import models, database
from app import utils
from jose import JWTError, jwt
from app.schemas import UserRole 
from app.schemas import UpdatePasswordRequest
from app.utils import get_current_user 

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
ALGORITHM = "HS256"

SECRET_KEY = "your_secret_key"



class ForgotPasswordRequest(BaseModel):
    email: str

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(database.get_db)):
    # 1️⃣ Check if user exists
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # 2️⃣ Generate a new random password
    new_password = utils.generate_random_password()

    # 3️⃣ Update the user's password in database
    user.password = utils.hash_password(new_password)
    db.commit()
    db.refresh(user)

    # 4️⃣ Send email to user
    try:
        utils.send_email(
            to_email=user.email,
            subject="Your New Password",
            body=f"Hello {user.username},\n\nYour new password is: {new_password}\n\nPlease login and change it immediately."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {"message": "New password has been sent to your email and updated in the system."}


@router.patch("/update-password")
def update_password(
    request: UpdatePasswordRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    # 1️⃣ Check old password
    if not utils.verify_password(request.oldpassword, current_user.password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # 2️⃣ Check new password and confirm password match
    if request.newpassword != request.confirmpassword:
        raise HTTPException(status_code=400, detail="New password and confirm password do not match")

    # 3️⃣ Hash new password and update in DB
    current_user.password = utils.hash_password(request.newpassword)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}

# ------------------ Signup ------------------ #
class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    role: UserRole # "customer" | "restaurant" | "delivery"

@router.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(database.get_db)):
    if user.role not in ["customer", "restaurant", "delivery"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Hash password
    hashed_password = utils.hash_password(user.password)

    db_user = models.User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully", "role": db_user.role}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(
        (models.User.username == form_data.username) | 
        (models.User.email == form_data.username)     # 👈 allow email as login
    ).first()

    if not user or not utils.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token_data = {"sub": user.username, "role": user.role}
    access_token = utils.create_access_token(token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }
