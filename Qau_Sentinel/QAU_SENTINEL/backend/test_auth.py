import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_login():
    print("=" * 50)
    print("TESTING LOGIN")
    print("=" * 50)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@qau.edu.pk",
            "password": "admin123"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        print("✅ Login successful!")
        print(f"Access Token: {data['access_token'][:50]}...")
        print(f"User: {data['user']['username']} ({data['user']['role']})")
        return data['access_token']
    else:
        print(f"❌ Login failed: {data}")
        return None

def test_protected_route(token):
    print("\n" + "=" * 50)
    print("TESTING PROTECTED ROUTE (/cameras)")
    print("=" * 50)
    
    response = requests.get(
        f"{BASE_URL}/cameras",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Protected route accessible!")
        data = response.json()
        print(f"Found {data.get('total', 0)} cameras")
    else:
        print(f"❌ Protected route failed: {response.json()}")

def test_unauthorized_access():
    print("\n" + "=" * 50)
    print("TESTING UNAUTHORIZED ACCESS (No Token)")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/cameras")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Correctly rejected unauthorized request!")
    else:
        print(f"❌ Unexpected status: {response.status_code}")

if __name__ == "__main__":
    # Test 1: Unauthorized access
    test_unauthorized_access()
    
    # Test 2: Login
    token = test_login()
    
    # Test 3: Access protected route
    if token:
        test_protected_route(token)