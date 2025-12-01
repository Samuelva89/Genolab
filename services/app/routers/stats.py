# Importaciones necesarias
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importamos nuestros módulos
from .. import crud
from ..dependencies import get_db

# --- Esquema de Respuesta para Estadísticas ---
class SummaryStats(BaseModel):
    totalOrganisms: int
    totalStrains: int
    totalAnalyses: int

# --- Creación del Router ---
router = APIRouter(
    prefix="/stats",
    tags=["statistics"],
)

# --- Endpoint para Estadísticas de Resumen ---
@router.get("/summary", response_model=SummaryStats)
def get_summary_stats(db: Session = Depends(get_db)):
    """
    Devuelve un resumen de las estadísticas totales del sistema:
    - Número total de organismos
    - Número total de cepas
    - Número total de análisis
    """
    total_organisms = crud.get_organisms_count(db)
    total_strains = crud.get_strains_count(db)
    total_analyses = crud.get_analyses_count(db)
    
    return {
        "totalOrganisms": total_organisms,
        "totalStrains": total_strains,
        "totalAnalyses": total_analyses,
    }
