# pydantic es la librería para validar los datos de la API.
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Any
from datetime import datetime

# --- ESQUEMAS BASE ---
# Estos esquemas definen los campos comunes y no incluyen relaciones complejas.

class OrganismBase(BaseModel):
    name: str
    genus: str
    species: str

class StrainBase(BaseModel):
    strain_name: str
    source: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class AnalysisBase(BaseModel):
    analysis_type: str
    results: Any

# --- ESQUEMAS PARA LA CREACIÓN DE DATOS (INPUT) ---
# Heredan de los base y añaden la información necesaria para crear un nuevo objeto.

class OrganismCreate(OrganismBase):
    pass

class StrainCreate(StrainBase):
    organism_id: int

class UserCreate(UserBase):
    is_admin: bool = False

class AnalysisCreate(AnalysisBase):
    strain_id: int

# --- ESQUEMAS PARA LA ACTUALIZACIÓN DE DATOS (INPUT) ---

class OrganismUpdate(BaseModel):
    name: Optional[str] = None
    genus: Optional[str] = None
    species: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    

# --- ESQUEMAS COMPLETOS PARA RESPUESTAS DE LA API (OUTPUT) ---
# Estos esquemas definen cómo se verán los datos cuando la API los devuelva.
# Aquí es donde controlamos los bucles de recursión.

# Esquema simple para Organism, para ser usado dentro de otros esquemas y evitar bucles.
# Este esquema representa un Organismo cuando se anida dentro de una Cepa,
# evitando la referencia circular a la lista de cepas del Organismo.
class OrganismInDB(OrganismBase):
    id: int
    model_config = {"from_attributes": True}

class Analysis(AnalysisBase):
    id: int
    owner_id: int
    strain_id: int
    timestamp: datetime
    model_config = {"from_attributes": True}

class Strain(StrainBase):
    id: int
    organism_id: int
    # Usamos el esquema simple OrganismInDB para evitar el bucle de recursión.
    organism: OrganismInDB
    analyses: List[Analysis] = []
    model_config = {"from_attributes": True}

class Organism(OrganismBase):
    id: int
    # Un organismo sí puede devolver la lista completa de sus cepas
    # cuando se solicita directamente o como parte de una respuesta de nivel superior.
    strains: List[Strain] = []
    model_config = {"from_attributes": True}

class User(UserBase):
    id: int
    name: Optional[str] = None
    analyses: List[Analysis] = []
    model_config = {"from_attributes": True}

# --- ESQUEMAS PARA AUTENTICACIÓN ---

# --- Reconstrucción de modelos ---
# Pydantic necesita esto para resolver las referencias anidadas.
Organism.model_rebuild()
Strain.model_rebuild()
