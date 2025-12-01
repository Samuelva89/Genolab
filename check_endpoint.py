"""
Script to test if the new download endpoint exists
"""
import requests

# Configura la URL base del backend
BASE_URL = "http://localhost:8000"

def check_endpoint_exists():
    """Check if the download endpoint is available"""
    try:
        # Try to access the specific download endpoint
        print("Checking if download endpoint exists...")
        # We'll try with a fake ID that should return 404 if the endpoint exists but analysis doesn't exist
        # or 404 "Not Found" if the endpoint doesn't exist
        response = requests.get(f"{BASE_URL}/api/analysis/999999999/download")

        if response.status_code == 404:
            # Check the content of the response
            if "Análisis no encontrado" in response.text or "Análisis no encontrado" in response.json().get("detail", ""):
                print("[OK] Endpoint exists but analysis not found (expected behavior)")
                return True
            elif response.json().get("detail") == "Not Found":
                print("[FAILED] Endpoint does not exist")
                return False
            else:
                print(f"[?] Unexpected response: {response.json()}")
                return False
        elif response.status_code == 200:
            print("[OK] Endpoint exists and returned file (unexpected for fake ID)")
            return True
        else:
            print(f"[?] Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking endpoint: {e}")
        return False

def main():
    print("=== Checking if download endpoint exists ===\n")
    exists = check_endpoint_exists()
    if exists:
        print("\n[OK] Download endpoint is available!")
        print("The endpoint was added successfully to the API.")
    else:
        print("\n[FAILED] Download endpoint is not available.")
        print("The API server may need to be restarted to pick up the changes.")

if __name__ == "__main__":
    main()