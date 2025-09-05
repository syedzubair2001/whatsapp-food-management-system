from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import models, database
import smtplib
import os
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from passlib.context import CryptContext


# ------------------ Password Hashing ------------------ #
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)


def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = os.getenv("SMTP_USERNAME")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")))
    if os.getenv("SMTP_USE_TLS") == "True":
        server.starttls()
    server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
    server.send_message(msg)
    server.quit()
    return True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ------------------ JWT Handling ------------------ #
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")  # fallback if not in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    """Decode JWT token"""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ------------------ OAuth2 Scheme for Swagger ------------------ #
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ------------------ Current User ------------------ #
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.User:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.username == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user  # <-- return User model

# ------------------ Role-based Access ------------------ #
# def role_required(required_role: str):
#     def dependency(current_user: models.User = Depends(get_current_user)):
#         if current_user.role != required_role:
#             raise HTTPException(status_code=403, detail="Not authorized for this action")
#         return current_user
#     return dependency




# ------------------ Role-based Access ------------------ #
def role_required(required_roles):
    """
    Accepts a single role as string OR multiple roles as list.
    Example:
        role_required("restaurant")
        role_required(["restaurant", "delivery"])
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def dependency(current_user=Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(status_code=403, detail="Not authorized for this action")
        return current_user

    return dependency
