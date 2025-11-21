from fastapi.testclient import TestClient
from io import BytesIO

from fastapi.testclient import TestClient
from io import BytesIO
from unittest.mock import patch, MagicMock

@patch('app.routers.analysis.process_fasta_count')
@patch('app.routers.analysis.s3_client')
def test_upload_fasta_for_analysis(mock_s3_client: MagicMock, mock_process_fasta_count: MagicMock, client: TestClient):
    """
    Test uploading a FASTA file for analysis.
    This is a unit test that mocks external S3 and Celery calls.
    """
    # 1. Configure Mocks
    # Mock the return value of the celery task's delay method
    mock_task = MagicMock()
    mock_task.id = "a-mock-task-id"
    mock_process_fasta_count.delay.return_value = mock_task

    # 2. Create a user (analysis owner)
    user_response = client.post("/api/users/", json={"email": "analyst@example.com", "password": "password"})
    assert user_response.status_code == 201
    
    # 3. Create an organism and a strain
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

    # 4. Prepare a fake FASTA file
    fake_fasta_content = b">seq1\nACGT\n>seq2\nGCTA"
    file_to_upload = ("test.fasta", BytesIO(fake_fasta_content), "text/plain")

    # 5. Upload the file to the analysis endpoint
    response = client.post(
        "/api/analysis/upload/fasta_count",
        data={"strain_id": strain_id},
        files={"file": file_to_upload},
    )

    # 6. Assert the response
    assert response.status_code == 202  # 202 Accepted
    data = response.json()
    assert data["message"] == "Análisis de conteo FASTA iniciado"
    assert data["task_id"] == "a-mock-task-id"

    # 7. Assert that our mocks were called correctly
    mock_s3_client.upload_fileobj.assert_called_once()
    mock_process_fasta_count.delay.assert_called_once()

