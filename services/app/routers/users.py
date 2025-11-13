# Importaciones necesarias
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

# Importamos nuestros módulos
from .. import crud, models, schemas
from ..dependencies import get_db

# --- Creación del Router ---
# Todas las rutas aquí definidas comenzarán con /users
router = APIRouter(
    prefix="/users",
    tags=["users"], # Etiqueta para la documentación
)

# --- Endpoint de Registro de Usuarios ---
@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario en el sistema.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado.")
    
    return crud.create_user(db=db, user=user)

# --- Endpoint para Obtener una Lista de Usuarios ---
@router.get("/", response_model=List[schemas.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Devuelve una lista de todos los usuarios.
    """
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# --- Endpoint para Contar Usuarios ---
@router.get("/count", response_model=int)
def get_users_count(
    db: Session = Depends(get_db)
):
    """
    Devuelve el número total de usuarios registrados en el sistema.
    """
    return db.query(models.User).count()

# --- Endpoint para Obtener un Usuario por ID ---
@router.get("/{user_id}", response_model=schemas.User)
def read_user(
    user_id: int, 
    db: Session = Depends(get_db)
):
    """
    Busca y devuelve un único usuario por su ID.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user

# --- Endpoint para Actualizar un Usuario ---
@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, 
    user_in: schemas.UserUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualiza la información de un usuario.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    updated_user = crud.update_user(db=db, user_id=user_id, user_in=user_in)
    return updated_user

# --- Endpoint para Hacer a un Usuario Administrador ---
@router.put("/{user_id}/make-admin", response_model=schemas.User)
def make_user_admin(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Establece el rol de administrador para un usuario específico.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    db_user.is_admin = True
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

# --- Endpoint para Eliminar un Usuario ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un usuario de la base de datos.
    Devuelve 204 No Content si la eliminación es exitosa.
    """
    deleted_user = crud.delete_user(db=db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)
