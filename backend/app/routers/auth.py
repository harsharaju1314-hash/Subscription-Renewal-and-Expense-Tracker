from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    decode_access_token,
    decode_refresh_token,
    RoleChecker,
)
from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.models.role import Role, UserRole
from backend.app.models.budget import Budget
from backend.app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")
    return user


def require_role(roles: list[str]):
    """Helper returning a dependency enforcing RBAC."""
    checker = RoleChecker(roles)
    def role_dependency(current_user: User = Depends(get_current_user)):
        checker(current_user)
        return current_user
    return role_dependency


def _build_user_response(user: User) -> UserResponse:
    user_roles = [ur.role.name for ur in user.user_roles if ur.role] if user.user_roles else ["USER"]
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        roles=user_roles,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegisterRequest, db: Session = Depends(get_db)):
    # Check if email or username exists
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken.",
        )

    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name or user_in.username,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign default USER role
    user_role_obj = db.query(Role).filter(Role.name == "USER").first()
    if not user_role_obj:
        user_role_obj = Role(name="USER", description="Standard User")
        db.add(user_role_obj)
        db.commit()
        db.refresh(user_role_obj)
    
    db.add(UserRole(user_id=user.id, role_id=user_role_obj.id))
    db.commit()
    db.refresh(user)

    # Create default budget for user
    default_budget = Budget(user_id=user.id, monthly_limit=250.00, alert_threshold_pct=80)
    db.add(default_budget)
    db.commit()

    user_roles = ["USER"]
    access_token = create_access_token(subject=user.id, roles=user_roles)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=_build_user_response(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            (User.email == login_in.username_or_email)
            | (User.username == login_in.username_or_email)
        )
        .first()
    )
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account.")

    user_roles = user.roles if user.roles else ["USER"]
    access_token = create_access_token(subject=user.id, roles=user_roles)
    refresh_token = create_refresh_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=_build_user_response(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(token_in: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_refresh_token(token_in.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer active or found.",
        )

    user_roles = user.roles if user.roles else ["USER"]
    new_access = create_access_token(subject=user.id, roles=user_roles)
    new_refresh = create_refresh_token(subject=user.id)
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user=_build_user_response(user),
    )


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": f"Successfully logged out user {current_user.username}."}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return _build_user_response(current_user)
