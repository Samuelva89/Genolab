from fastapi.testclient import TestClient
from io import BytesIO

def test_upload_fasta_for_analysis(client: TestClient):
    """
    Test uploading a FASTA file for analysis.
    This is a basic integration test to ensure the endpoint is reachable
    and returns a task ID. It does not test the Celery worker itself.
    """
    # 1. Create a user (analysis owner)
    user_response = client.post("/api/users/", json={"email": "analyst@example.com", "password": "password"})
    assert user_response.status_code == 201
    
    # 2. Create an organism and a strain
    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "Analysis Organism", "genus": "Analysis", "species": "organism"},
    )
    assert org_response.status_code == 200
    organism_id = org_response.json()["id"]

    strain_response = client.post(
        "/api/ceparium/strains/",
        json={"strain_name": "Strain for Analysis", "source": "Test Lab", "organism_id": organism_id},
    )
    assert strain_response.status_code == 200
    strain_id = strain_response.json()["id"]

    # 3. Prepare a fake FASTA file
    fake_fasta_content = b">seq1\nACGT\n>seq2\nGCTA"
    file_to_upload = ("test.fasta", BytesIO(fake_fasta_content), "text/plain")

    # 4. Upload the file to the analysis endpoint
    response = client.post(
        "/api/analysis/upload/fasta_count",
        data={"strain_id": strain_id},
        files={"file": file_to_upload},
    )

    # 5. Assert the response
    assert response.status_code == 202  # 202 Accepted
    data = response.json()
    assert "message" in data
    assert "task_id" in data
    assert data["message"] == "Análisis de conteo FASTA iniciado"
