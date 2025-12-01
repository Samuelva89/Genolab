# Importaciones necesarias
from sqlalchemy.orm import Session
from . import models, schemas


# --- Funciones para Usuarios ---

def get_user_by_email(db: Session, email: str):
    """Devuelve un usuario por su email."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Crea un nuevo usuario."""
    db_user = models.User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de usuarios."""
    return db.query(models.User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    """Devuelve un usuario por su ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()

def update_user(db: Session, user_id: int, user_in: schemas.UserUpdate):
    """Actualiza un usuario existente."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        # Solo actualizamos los campos que no sean None
        if user_in.email is not None:
            db_user.email = user_in.email
        if user_in.name is not None:
            db_user.name = user_in.name
        if user_in.is_active is not None:
            db_user.is_active = user_in.is_active

        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Elimina un usuario por su ID."""
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# --- Funciones para Organismos ---

def get_organism_by_name(db: Session, name: str):
    """Devuelve un organismo por su nombre."""
    return db.query(models.Organism).filter(models.Organism.name == name).first()

def create_organism(db: Session, organism: schemas.OrganismCreate):
    """Crea un nuevo organismo."""
    db_organism = models.Organism(name=organism.name, genus=organism.genus, species=organism.species)
    db.add(db_organism)
    db.commit()
    db.refresh(db_organism)
    return db_organism

def get_organisms(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de organismos."""
    return db.query(models.Organism).offset(skip).limit(limit).all()

def get_organism(db: Session, organism_id: int):
    """Devuelve un organismo por su ID."""
    return db.query(models.Organism).filter(models.Organism.id == organism_id).first()

def update_organism(db: Session, organism_id: int, organism_in: schemas.OrganismUpdate):
    """Actualiza un organismo existente."""
    db_organism = db.query(models.Organism).filter(models.Organism.id == organism_id).first()
    if db_organism:
        if organism_in.name is not None:
            db_organism.name = organism_in.name
        if organism_in.genus is not None:
            db_organism.genus = organism_in.genus
        if organism_in.species is not None:
            db_organism.species = organism_in.species

        db.commit()
        db.refresh(db_organism)
    return db_organism

def delete_organism(db: Session, organism_id: int):
    """Elimina un organismo por su ID."""
    db_organism = db.query(models.Organism).filter(models.Organism.id == organism_id).first()
    if db_organism:
        db.delete(db_organism)
        db.commit()
    return db_organism


# --- Funciones para Cepas ---

def get_strains_by_organism(db: Session, organism_id: int):
    """Devuelve una lista de cepas para un organismo específico."""
    return db.query(models.Strain).filter(models.Strain.organism_id == organism_id).all()

def create_strain(db: Session, strain: schemas.StrainCreate):
    """Crea una nueva cepa."""
    db_strain = models.Strain(
        strain_name=strain.strain_name,
        source=strain.source,
        organism_id=strain.organism_id
    )
    db.add(db_strain)
    db.commit()
    db.refresh(db_strain)
    return db_strain

def get_strains(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de cepas."""
    return db.query(models.Strain).offset(skip).limit(limit).all()

def get_strain(db: Session, strain_id: int):
    """Devuelve una cepa por su ID."""
    return db.query(models.Strain).filter(models.Strain.id == strain_id).first()


# --- Funciones para Análisis ---

def create_analysis(db: Session, analysis: schemas.AnalysisCreate, owner_id: int):
    """Crea un nuevo análisis."""
    db_analysis = models.Analysis(
        analysis_type=analysis.analysis_type,
        results=analysis.results,
        strain_id=analysis.strain_id,
        owner_id=owner_id,
        file_url=analysis.file_url
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def get_analysis(db: Session, analysis_id: int):
    """Devuelve un análisis por su ID."""
    return db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()

def get_analyses(db: Session, skip: int = 0, limit: int = 100):
    """Devuelve una lista de análisis."""
    return db.query(models.Analysis).offset(skip).limit(limit).all()

def get_analyses_by_strain(db: Session, strain_id: int, skip: int = 0, limit: int = 100):
    """
    Devuelve una lista de análisis para una cepa específica.
    """
    return db.query(models.Analysis).filter(models.Analysis.strain_id == strain_id).offset(skip).limit(limit).all()

# --- Funciones de Conteo para Estadísticas ---

def get_organisms_count(db: Session) -> int:
    """Devuelve el número total de organismos."""
    return db.query(models.Organism.id).count()

def get_strains_count(db: Session) -> int:
    """Devuelve el número total de cepas."""
    return db.query(models.Strain.id).count()

def get_analyses_count(db: Session) -> int:
    """Devuelve el número total de análisis."""
    return db.query(models.Analysis.id).count()
