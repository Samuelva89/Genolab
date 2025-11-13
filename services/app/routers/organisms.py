# Importaciones necesarias
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# Importamos nuestros módulos
from .. import crud, schemas
from ..dependencies import get_db

# --- Creación del Router ---
# Todas las rutas aquí definidas comenzarán con /ceparium
# Usamos 'ceparium' como prefijo para agrupar todo lo relacionado con organismos y cepas.
router = APIRouter(
    prefix="/ceparium",
    tags=["ceparium"], # Etiqueta para la documentación
)

# --- Endpoints para Organismos ---

@router.post("/organisms/", response_model=schemas.Organism)
def create_organism(
    organism: schemas.OrganismCreate, 
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo organismo.
    """    
    # Verificamos si ya existe un organismo con ese nombre para evitar duplicados.
    db_organism = crud.get_organism_by_name(db, name=organism.name)
    if db_organism:
        raise HTTPException(status_code=400, detail="El nombre del organismo ya existe.")
    
    return crud.create_organism(db=db, organism=organism)

@router.get("/organisms/", response_model=List[schemas.Organism])
def read_organisms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Devuelve una lista de todos los organismos.
    Ruta pública.
    """
    organisms = crud.get_organisms(db, skip=skip, limit=limit)
    return organisms

@router.get("/organisms/{organism_id}", response_model=schemas.Organism)
def read_organism(organism_id: int, db: Session = Depends(get_db)):
    """
    Devuelve un único organismo por su ID.
    Ruta pública.
    """
    # Usamos la función que ya existe en crud.py para buscar el organismo
    db_organism = crud.get_organism(db, organism_id=organism_id)
    
    # Si no se encuentra, devolvemos un error 404 "Not Found"
    if db_organism is None:
        raise HTTPException(status_code=404, detail="Organismo no encontrado.")
        
    return db_organism

@router.get("/organisms/{organism_id}/strains", response_model=List[schemas.Strain])
def read_strains_for_organism(organism_id: int, db: Session = Depends(get_db)):
    """
    Devuelve una lista de todas las cepas para un organismo específico.
    Ruta pública.
    """
    strains = crud.get_strains_by_organism(db, organism_id=organism_id)
    return strains

# --- Endpoints para Cepas ---

@router.post("/strains/", response_model=schemas.Strain)
def create_strain(
    strain: schemas.StrainCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva cepa.
    """
    
    # Verificamos que el 'organism_id' que se proporciona para la cepa realmente exista.
    db_organism = crud.get_organism(db, organism_id=strain.organism_id)
    if not db_organism:
        raise HTTPException(status_code=404, detail="El organismo especificado no existe.")

    return crud.create_strain(db=db, strain=strain)

@router.get("/strains/", response_model=List[schemas.Strain])
def read_strains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Devuelve una lista de todas las cepas.
    Ruta pública.
    """
    strains = crud.get_strains(db, skip=skip, limit=limit)
    return strains

@router.put("/organisms/{organism_id}", response_model=schemas.Organism)
def update_organism(
    organism_id: int,
    organism_in: schemas.OrganismUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un organismo existente.
    """

    # Llama a la función del CRUD para hacer la actualización.
    db_organism = crud.update_organism(db, organism_id=organism_id, organism_in=organism_in)
    
    if db_organism is None:
        raise HTTPException(status_code=404, detail="Organismo no encontrado.")
        
    return db_organism


@router.delete("/organisms/{organism_id}", response_model=schemas.Organism)
def delete_organism(
    organism_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un organismo.
    """

    # Llama a la función del CRUD para eliminar.
    db_organism = crud.delete_organism(db, organism_id=organism_id)
    
    if db_organism is None:
        raise HTTPException(status_code=404, detail="Organismo no encontrado.")
        
    return db_organism