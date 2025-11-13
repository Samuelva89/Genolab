from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..dependencies import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_new_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint público para registrar un nuevo usuario.
    Cualquier usuario creado será un usuario estándar.
    Devuelve el usuario creado tras el registro exitoso.
    """
    # Check if email is already registered
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    # Create the user (password hashing is handled in crud.py)
    # The is_admin flag will be False by default based on the model definition.
    try:
        new_user = crud.create_user(db=db, user=user_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {e}")

    return new_user