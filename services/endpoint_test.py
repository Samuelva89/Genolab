import sys
import os

# Add services directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

result_file = 'endpoint_test_results.txt'
with open(result_file, 'w') as f:
    try:
        from app.main import app
        from fastapi.testclient import TestClient

        # Create a test client to simulate requests
        client = TestClient(app)

        # Test the stats endpoint
        f.write('Testing stats endpoint...\n')
        response = client.get('/api/stats/summary')

        f.write(f'Status Code: {response.status_code}\n')
        f.write(f'Response: {response.text}\n')

        if response.status_code == 200:
            f.write('SUCCESS: Stats endpoint is working correctly!\n')
            f.write(f'Response JSON: {str(response.json())}\n')
        else:
            f.write('ERROR: Stats endpoint is not working\n')
            
            # Let's try to see what endpoints are available
            f.write('\nTrying to get the root endpoint...\n')
            root_response = client.get('/')
            f.write(f'Root status: {root_response.status_code}\n')
            f.write(f'Root response: {root_response.text}\n')
            
            # Let's try to see all available routes
            f.write('\nListing all available routes:\n')
            for route in app.routes:
                if hasattr(route, 'path'):
                    f.write(f'Route: {route.path}\n')
    except Exception as e:
        f.write(f'Error testing endpoints: {e}\n')
        import traceback
        f.write(traceback.format_exc() + '\n')

print(f'Endpoint test results written to {result_file}')