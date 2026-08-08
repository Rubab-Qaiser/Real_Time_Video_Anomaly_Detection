import requests

# Login to get token
login_response = requests.post(
    "http://localhost:5000/api/auth/login",
    json={"email": "admin@qau.edu.pk", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.json())
    exit()

token = login_response.json()["access_token"]
print(f"✅ Got token: {token[:50]}...")

# Test cameras endpoint
cameras_response = requests.get(
    "http://localhost:5000/api/cameras",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Cameras endpoint: {cameras_response.status_code}")

if cameras_response.status_code == 200:
    print(f"✅ Cameras: {cameras_response.json()}")
else:
    print(f"❌ Error: {cameras_response.text}")

# Test live stream
stream_response = requests.get(
    "http://localhost:5000/api/cameras/1/live",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Stream endpoint: {stream_response.status_code}")
# Test live stream
print("\n🔴 Testing live stream...")
stream_response = requests.get(
    "http://localhost:5000/api/cameras/1/live",
    headers={"Authorization": f"Bearer {token}"},
    stream=True  # Important for streaming
)

print(f"Stream endpoint status: {stream_response.status_code}")

if stream_response.status_code == 200:
    print("✅ Stream is working!")
    print(f"   Content-Type: {stream_response.headers.get('Content-Type')}")
    # Read first few bytes to verify
    chunk = stream_response.raw.read(100)
    print(f"   First 100 bytes: {chunk[:50]}...")
else:
    print(f"❌ Stream error: {stream_response.text}")