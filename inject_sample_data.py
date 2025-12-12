"""
Script para inyectar datos completos de ejemplo a la base de datos
"""
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta
import random

# Añadir la carpeta de servicios al path para poder importar
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def inject_sample_data():
    # Conectar a la base de datos
    db_path = os.path.join("services", "genolab.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Inyectando datos de ejemplo completos...")
    
    # Eliminar datos existentes para tener un estado limpio
    print("Limpiando datos existentes...")
    cursor.execute("DELETE FROM analyses")
    cursor.execute("DELETE FROM strains")
    cursor.execute("DELETE FROM organisms")
    cursor.execute("DELETE FROM users")
    
    # Insertar usuarios
    print("Insertando usuarios...")
    cursor.execute(
        "INSERT INTO users (id, email, name, is_active) VALUES (?, ?, ?, ?)",
        (1, "admin@genolab.com", "Administrador Principal", 1)
    )
    
    # Organismos de ejemplo
    print("Insertando organismos...")
    organisms_data = [
        (1, "Escherichia coli", "Escherichia", "coli"),
        (2, "Saccharomyces cerevisiae", "Saccharomyces", "cerevisiae"),
        (3, "Candida albicans", "Candida", "albicans"),
        (4, "Bacillus subtilis", "Bacillus", "subtilis"),
        (5, "Aspergillus niger", "Aspergillus", "niger"),
        (6, "Staphylococcus aureus", "Staphylococcus", "aureus"),
    ]
    
    for org_data in organisms_data:
        cursor.execute(
            "INSERT INTO organisms (id, name, genus, species) VALUES (?, ?, ?, ?)",
            org_data
        )
    
    # Cepas de ejemplo
    print("Insertando cepas...")
    strains_data = [
        (1, "E. coli K-12", "Laboratory strain", 1),
        (2, "E. coli DH5α", "Cloning strain", 1),
        (3, "S. cerevisiae BY4741", "Laboratory strain", 2),
        (4, "C. albicans SC5314", "Reference strain", 3),
        (5, "B. subtilis 168", "Laboratory strain", 4),
        (6, "A. niger ATCC 10861", "Wild type", 5),
        (7, "S. aureus NCTC 8325", "Reference strain", 6),
        (8, "E. coli BL21(DE3)", "Expression strain", 1),
        (9, "S. cerevisiae INVSc1", "Competent cells", 2),
        (10, "C. albicans BWP17", "Ura- auxotrophic", 3),
    ]
    
    for strain_data in strains_data:
        cursor.execute(
            "INSERT INTO strains (id, strain_name, source, organism_id) VALUES (?, ?, ?, ?)",
            strain_data
        )
    
    # Generar análisis de ejemplo
    print("Insertando análisis...")
    analysis_types = ['fasta_count', 'fasta_gc_content', 'gff_stats', 'genbank_stats', 'fastq_stats', 'raw_file']
    
    analysis_count = 1
    for strain_id in range(1, 11):
        # Cada cepa tendrá entre 3-7 análisis de diferentes tipos
        num_analyses = random.randint(3, 7)
        
        for _ in range(num_analyses):
            analysis_type = random.choice(analysis_types)
            
            # Generar resultados según el tipo de análisis
            if analysis_type == 'fasta_count':
                results = {
                    "sequence_count": random.randint(1, 10),
                    "filename": f"sample_{analysis_count}_fasta.fasta"
                }
            elif analysis_type == 'fasta_gc_content':
                sequence_count = random.randint(1, 5)
                individual_gc = [round(random.uniform(30, 70), 2) for _ in range(sequence_count)]
                results = {
                    "filename": f"sample_{analysis_count}_fasta.fasta",
                    "sequence_count": sequence_count,
                    "average_gc_content": round(sum(individual_gc) / len(individual_gc), 2),
                    "individual_gc_contents": individual_gc
                }
            elif analysis_type == 'gff_stats':
                results = {
                    "filename": f"sample_{analysis_count}.gff",
                    "feature_counts": {
                        "gene": random.randint(1, 100),
                        "CDS": random.randint(1, 80),
                        "exon": random.randint(1, 150),
                        "intron": random.randint(0, 50),
                        "mRNA": random.randint(1, 90)
                    }
                }
            elif analysis_type == 'genbank_stats':
                results = {
                    "filename": f"sample_{analysis_count}.gbk",
                    "sequence_count": 1,
                    "main_record_id": f"U{random.randint(10000, 99999)}",
                    "description": f"Sample sequence from organism {strain_id}",
                    "sequence_length": random.randint(1000, 10000),
                    "feature_count": random.randint(1, 50),
                    "molecule_type": "DNA",
                    "topology": random.choice(["linear", "circular"])
                }
            elif analysis_type == 'fastq_stats':
                results = {
                    "filename": f"sample_{analysis_count}.fastq",
                    "sequence_count": random.randint(1, 20),
                    "avg_sequence_length": random.randint(50, 300),
                    "min_length": random.randint(30, 200),
                    "max_length": random.randint(100, 400),
                    "overall_avg_quality": round(random.uniform(25, 40), 1)
                }
            else:  # raw_file
                extensions = ['.fasta', '.gbk', '.gff', '.fastq']
                ext = random.choice(extensions)
                results = {
                    "filename": f"sample_{analysis_count}{ext}",
                    "file_size": random.randint(50, 2000),
                    "upload_status": "completed",
                    "message": "Archivo subido directamente sin análisis"
                }
            
            # Generar fecha aleatoria en los últimos 30 días
            days_ago = random.randint(0, 30)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            cursor.execute(
                "INSERT INTO analyses (id, analysis_type, results, file_url, timestamp, strain_id, owner_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    analysis_count,
                    analysis_type,
                    json.dumps(results),
                    f"http://minio:9000/genolab-bucket/uploads/sample_{analysis_count}_{analysis_type}{os.path.splitext(results['filename'])[1] if 'filename' in results else '.fasta'}",
                    timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    strain_id,
                    1
                )
            )
            analysis_count += 1
    
    # Confirmar cambios
    conn.commit()
    
    # Verificar lo que se insertó
    cursor.execute("SELECT COUNT(*) FROM organisms")
    org_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM strains")
    strain_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM analyses")
    analysis_count = cursor.fetchone()[0]
    
    print(f"Datos inyectados exitosamente:")
    print(f"- {org_count} organismos")
    print(f"- {strain_count} cepas") 
    print(f"- {analysis_count} análisis")
    
    conn.close()
    print("Inyección de datos completada!")

if __name__ == "__main__":
    inject_sample_data()