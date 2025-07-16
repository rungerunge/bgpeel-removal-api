import requests
import base64
from PIL import Image
import io
import os

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check test passed")

def test_root_endpoint():
    """Test the root endpoint"""
    response = requests.get("http://localhost:8000/")
    assert response.status_code == 200
    assert "name" in response.json()
    assert "version" in response.json()
    print("✅ Root endpoint test passed")

def test_background_removal():
    """Test the background removal endpoint"""
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Test base64 response
    files = {'file': ('test.png', img_byte_arr, 'image/png')}
    response = requests.post(
        "http://localhost:8000/remove-background",
        files=files,
        data={'return_type': 'base64'}
    )
    assert response.status_code == 200
    assert "image" in response.json()
    print("✅ Background removal (base64) test passed")

    # Test direct image response
    response = requests.post(
        "http://localhost:8000/remove-background",
        files=files,
        data={'return_type': 'direct'}
    )
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/png'
    print("✅ Background removal (direct) test passed")

def test_invalid_file_type():
    """Test invalid file type handling"""
    # Create a text file
    files = {'file': ('test.txt', b'test content', 'text/plain')}
    response = requests.post(
        "http://localhost:8000/remove-background",
        files=files
    )
    assert response.status_code == 415
    print("✅ Invalid file type test passed")

def run_tests():
    """Run all tests"""
    print("Running API tests...")
    try:
        test_health_check()
        test_root_endpoint()
        test_background_removal()
        test_invalid_file_type()
        print("\nAll tests passed! 🎉")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API. Make sure it's running on http://localhost:8000")

if __name__ == "__main__":
    run_tests() 