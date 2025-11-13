from fastapi.testclient import TestClient

def test_create_organism(client: TestClient):
    """
    Test creating a new organism.
    """
    response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "Saccharomyces cerevisiae", "genus": "Saccharomyces", "species": "cerevisiae"},
    )
    assert response.status_code == 200  # Note: The endpoint returns 200, not 201
    data = response.json()
    assert data["name"] == "Saccharomyces cerevisiae"
    assert "id" in data

def test_read_organisms(client: TestClient):
    """
    Test reading a list of organisms.
    """
    client.post("/api/ceparium/organisms/", json={"name": "Test Fungus", "genus": "Test", "species": "fungus"})
    
    response = client.get("/api/ceparium/organisms/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(org["name"] == "Test Fungus" for org in data)

def test_create_strain(client: TestClient):
    """
    Test creating a new strain for an organism.
    """
    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "Parent Organism", "genus": "Parent", "species": "organism"},
    )
    organism_id = org_response.json()["id"]

    strain_response = client.post(
        "/api/ceparium/strains/",
        json={"strain_name": "Strain A1", "source": "Lab X", "organism_id": organism_id},
    )
    assert strain_response.status_code == 200
    data = strain_response.json()
    assert data["strain_name"] == "Strain A1"
    assert data["organism_id"] == organism_id

def test_read_strains(client: TestClient):
    """
    Test reading a list of all strains.
    """
    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "Another Parent", "genus": "Another", "species": "parent"},
    )
    organism_id = org_response.json()["id"]
    client.post("/api/ceparium/strains/", json={"strain_name": "Strain B2", "source": "Lab Y", "organism_id": organism_id})

    response = client.get("/api/ceparium/strains/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["strain_name"] == "Strain B2" for s in data)

def test_update_organism(client: TestClient):
    """
    Test updating an existing organism.
    """
    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "To Update", "genus": "Old Genus", "species": "Old Species"},
    )
    organism_id = org_response.json()["id"]

    update_response = client.put(
        f"/api/ceparium/organisms/{organism_id}",
        json={"name": "Updated Name"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["genus"] == "Old Genus" # Check that other fields are preserved

def test_delete_organism(client: TestClient):
    """
    Test deleting an organism.
    """
    org_response = client.post(
        "/api/ceparium/organisms/",
        json={"name": "To Delete", "genus": "Temp", "species": "delete"},
    )
    organism_id = org_response.json()["id"]

    delete_response = client.delete(f"/api/ceparium/organisms/{organism_id}")
    assert delete_response.status_code == 200 # The endpoint returns 200 with the deleted object

    # Verify it's gone
    get_response = client.get(f"/api/ceparium/organisms/{organism_id}")
    assert get_response.status_code == 404
