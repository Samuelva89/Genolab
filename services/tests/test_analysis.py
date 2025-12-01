from fastapi.testclient import TestClient
from io import BytesIO
from unittest.mock import patch, MagicMock

# Import the dependency we want to override and the app
from app.routers.analysis import get_s3_client
from app.main import app

# 1. Create a mock S3 client and the override function
mock_s3_client = MagicMock()

def override_get_s3_client():
    """Dependency override function that returns our mock S3 client."""
    return mock_s3_client

# 2. Apply the override to the main app instance
app.dependency_overrides[get_s3_client] = override_get_s3_client


@patch('app.routers.analysis.process_fasta_count')
def test_upload_fasta_for_analysis(mock_process_fasta_count: MagicMock, client: TestClient):
    """
    Test uploading a FASTA file for analysis.
    This is a unit test that mocks external S3 (via dependency override) and Celery calls.
    """
    # 1. Reset and Configure Mocks for a clean test run
    mock_s3_client.reset_mock()
    mock_task = MagicMock()
    mock_task.id = "a-mock-task-id"
    mock_process_fasta_count.delay.return_value = mock_task

    # 2. Create prerequisite data: a user, an organism, and a strain
    user_response = client.post(
        "/api/users/",
        json={"email": "analyst@example.com", "name": "Test Analyst"},
    )
    assert user_response.status_code == 201, f"Failed to create user: {user_response.text}"

    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "Analysis Organism", "genus": "Analysis", "species": "organism"},
    )
    assert org_response.status_code == 200, f"Failed to create organism: {org_response.text}"
    organism_id = org_response.json()["id"]

    strain_response = client.post(
        "/api/ceparium/strains/",
        json={"strain_name": "Strain for Analysis", "source": "Test Lab", "organism_id": organism_id},
    )
    assert strain_response.status_code == 200, f"Failed to create strain: {strain_response.text}"
    strain_id = strain_response.json()["id"]

    # 3. Prepare a fake FASTA file for upload
    fake_fasta_content = b">seq1\nACGT\n>seq2\nGCTA"
    file_to_upload = ("test.fasta", BytesIO(fake_fasta_content), "text/plain")

    # 4. Upload the file to the analysis endpoint
    response = client.post(
        "/api/analysis/upload/fasta_count",
        data={"strain_id": strain_id},
        files={"file": file_to_upload},
    )

    # 5. Assert the response from the endpoint
    assert response.status_code == 202, f"Expected 202, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["message"] == "Análisis de conteo FASTA iniciado"
    assert data["task_id"] == "a-mock-task-id"

    # 6. Assert that our mocks were called as expected
    mock_s3_client.upload_fileobj.assert_called_once()
    mock_process_fasta_count.delay.assert_called_once()
