# Importamos las herramientas de SQLAlchemy y nuestros modelos y esquemas.
from sqlalchemy.orm import Session
from . import models, schemas

# --- CRUD para Usuarios ---

def get_user(db: Session, user_id: int):
    """
    Busca y devuelve un usuario por su ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Devuelve una lista de usuarios de la base de datos.

    Args:
        db (Session): La sesión de la base de datos.
        skip (int): El número de registros a saltar (para paginación).
        limit (int): El número máximo de registros a devolver.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user_by_email(db: Session, email: str):
    """
    Busca y devuelve un usuario por su dirección de email.

    Args:
        db (Session): La sesión de la base de datos inyectada por FastAPI.
        email (str): El email del usuario a buscar.

    Returns:
        models.User | None: El objeto usuario si se encuentra, o None si no existe.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario en la base de datos.

    Args:
        db (Session): La sesión de la base de datos.
        user (schemas.UserCreate): Los datos del nuevo usuario (email, name).

    Returns:
        models.User: El objeto usuario que se acaba de crear.
    """
    db_user = models.User(email=user.email, name=user.name, is_active=True)
    # db_user = models.User(email=user.email, name=user.name, is_active=True, is_admin=user.is_admin)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_in: schemas.UserUpdate):
    """
    Actualiza la información de un usuario en la base de datos.
    """
    # Obtenemos el usuario existente de la BD.
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None # O lanzar una excepción si se prefiere

    # Obtenemos los datos enviados en la petición como un diccionario.
    # exclude_unset=True significa que solo incluiremos los campos que el cliente envió.
    update_data = user_in.model_dump(exclude_unset=True)

    # Iteramos sobre los demás campos y los actualizamos en el objeto de la BD.
    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """
    Elimina un usuario de la base de datos.
    """
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        return None

    db.delete(db_user)
    db.commit()
    return db_user

# --- CRUD para Organismos ---

def get_organism(db: Session, organism_id: int):
    """Busca un organismo por su ID."""
    return db.query(models.Organism).filter(models.Organism.id == organism_id).first()

def get_organism_by_name(db: Session, name: str):
    """Busca un organismo por su nombre."""
    return db.query(models.Organism).filter(models.Organism.name == name).first()

def get_organisms(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de organismos."""
    return db.query(models.Organism).offset(skip).limit(limit).all()

def create_organism(db: Session, organism: schemas.OrganismCreate):
    """
    Crea un nuevo organismo en la base de datos."""
    db_organism = models.Organism(**organism.model_dump())
    db.add(db_organism)
    db.commit()
    db.refresh(db_organism)
    return db_organism

def update_organism(db: Session, organism_id: int, organism_in: schemas.OrganismUpdate):
    """
    Actualiza la información de un organismo en la base de datos.
    """
    # Busca el organismo existente en la base de datos.
    db_organism = get_organism(db, organism_id=organism_id)
    if not db_organism:
        return None # El organismo no existe

    # Convierte los datos de entrada a un diccionario, excluyendo los que no se enviaron.
    update_data = organism_in.model_dump(exclude_unset=True)

    # Actualiza los campos del objeto de la base de datos con los nuevos valores.
    for field, value in update_data.items():
        setattr(db_organism, field, value)

    # Guarda los cambios en la base de datos.
    db.add(db_organism)
    db.commit()
    db.refresh(db_organism)
    return db_organism

def delete_organism(db: Session, organism_id: int):
    """
    Elimina un organismo de la base de datos.
    """
    # Busca el organismo que se va a eliminar.
    db_organism = get_organism(db, organism_id=organism_id)
    if not db_organism:
        return None # No se encontró, no hay nada que eliminar.

    # Elimina el objeto de la sesión de la base de datos.
    db.delete(db_organism)
    db.commit()
    # Devuelve el objeto eliminado (ya no está en la BD, pero lo tenemos en memoria).
    return db_organism

# --- CRUD para Cepas (Strains) ---

def get_strains(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de todas las cepas."""
    return db.query(models.Strain).offset(skip).limit(limit).all()

def get_strains_by_organism(db: Session, organism_id: int, skip: int = 0, limit: int = 100):
    """Devuelve una lista de cepas para un organismo específico."""
    return db.query(models.Strain).filter(models.Strain.organism_id == organism_id).offset(skip).limit(limit).all()

def get_strain(db: Session, strain_id: int):
    """
    Busca y devuelve una cepa específica por su ID.

    Args:
        db (Session): La sesión de la base de datos.
        strain_id (int): El ID de la cepa a buscar.

    Returns:
        models.Strain | None: El objeto Strain si se encuentra, o None si no existe.
    """
    return db.query(models.Strain).filter(models.Strain.id == strain_id).first()


def create_strain(db: Session, strain: schemas.StrainCreate):
    """
    Crea una nueva cepa, asociada a un organismo."""
    db_strain = models.Strain(**strain.model_dump())
    db.add(db_strain)
    db.commit()
    db.refresh(db_strain)
    return db_strain

# --- CRUD para Análisis (Analyses) ---

def get_analyses(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de todos los análisis."""
    return db.query(models.Analysis).offset(skip).limit(limit).all()

def get_analysis(db: Session, analysis_id: int):
    """
    Busca y devuelve un análisis específico por su ID.
    """
    return db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()

def create_analysis(db: Session, analysis: schemas.AnalysisCreate, owner_id: int):
    """
    Crea un nuevo registro de análisis en la base de datos.

    Args:
        db (Session): La sesión de la base de datos.
        analysis (schemas.AnalysisCreate): Los datos del análisis (tipo, resultados, strain_id).
        owner_id (int): El ID del usuario propietario del análisis.
    """
    # Creamos el objeto del modelo SQLAlchemy, combinando los datos del esquema
    # con el owner_id que hemos pasado por separado.
    db_analysis = models.Analysis(**analysis.model_dump(), owner_id=owner_id)
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_analyses_by_strain(db: Session, strain_id: int, skip: int = 0, limit: int = 100):
    """
    Devuelve una lista de análisis para una cepa específica.
    """
    return db.query(models.Analysis).filter(models.Analysis.strain_id == strain_id).offset(skip).limit(limit).all()