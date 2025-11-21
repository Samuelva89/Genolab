# Importaciones necesarias de SQLAlchemy, la librería que nos permite hablar con la base de datos usando Python.
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func # Para obtener la fecha y hora actual de la base de datos

# Importamos 'Base' desde nuestro propio archivo 'database.py'.
# Todos nuestros modelos de base de datos heredarán de esta clase.
from .database import Base

# --- MODELO DE USUARIO ---
# Define la tabla 'users' en la base de datos.
class User(Base):
    # Nombre de la tabla en la base de datos.
    __tablename__ = "users"

    # --- Columnas de la tabla ---
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    # is_admin = Column(Boolean, default=False)  # Comentado temporalmente - no se requiere autenticación

    # --- Relación con Analysis ---
    # Un usuario puede tener muchos análisis.
    analyses = relationship("Analysis", back_populates="owner")

# --- MODELO DE ORGANISMO ---
# Define la tabla 'organisms' para almacenar las especies.
class Organism(Base):
    __tablename__ = "organisms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    genus = Column(String, index=True)
    species = Column(String, index=True)

    strains = relationship("Strain", back_populates="organism")

# --- MODELO DE CEPA ---
# Define la tabla 'strains' para el cepario.
class Strain(Base):
    __tablename__ = "strains"

    id = Column(Integer, primary_key=True, index=True)
    strain_name = Column(String, index=True)
    source = Column(String)
    organism_id = Column(Integer, ForeignKey("organisms.id"))

    organism = relationship("Organism", back_populates="strains")

    # --- Relación con Analysis ---
    # Una cepa puede tener muchos análisis asociados.
    analyses = relationship("Analysis", back_populates="strain")

# --- MODELO DE ANÁLISIS ---
# Define la tabla 'analyses' para guardar los resultados de los análisis.
class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)

    # Tipo de análisis realizado (ej: "fasta_count").
    analysis_type = Column(String, index=True, nullable=False)

    # Campo JSON para guardar un diccionario flexible de resultados.
    # Esta es la clave para que el modelo sea extensible a futuro.
    results = Column(JSON, nullable=False)

    # Columna para guardar la URL del archivo en el almacenamiento de objetos (MinIO)
    file_url = Column(String(1024), nullable=True)

    # Fecha y hora en que se creó el registro. Se autogenera por la BD.
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # --- Llaves Foráneas ---
    # Conecta el análisis con la cepa correspondiente.
    strain_id = Column(Integer, ForeignKey("strains.id"), nullable=False)
    # Conecta el análisis con el usuario que lo realizó.
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # --- Relaciones ---
    # Permite acceder al objeto 'Strain' completo desde un análisis.
    strain = relationship("Strain", back_populates="analyses")
    # Permite acceder al objeto 'User' (propietario) completo desde un análisis.
    owner = relationship("User", back_populates="analyses")