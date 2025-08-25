#!/usr/bin/env python3
"""
Debug script to examine the actual error response format
"""

import requests
import json

BASE_URL = "https://polaris-requirements.preview.emergentagent.com/api"

# Test invalid credentials
invalid_payload = {
    "email": "invalid@example.com",
    "password": "wrongpassword"
}

print("Testing invalid credentials...")
response = requests.post(f"{BASE_URL}/auth/login", json=invalid_payload)
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Text: {response.text}")

try:
    json_response = response.json()
    print(f"JSON Response: {json.dumps(json_response, indent=2)}")
except:
    print("Response is not valid JSON")

print("\n" + "="*50 + "\n")

# Test wrong password for existing user
wrong_password_payload = {
    "email": "client.qa@polaris.example.com",
    "password": "wrongpassword123"
}

print("Testing wrong password for existing user...")
response = requests.post(f"{BASE_URL}/auth/login", json=wrong_password_payload)
print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")
print(f"Response Text: {response.text}")

try:
    json_response = response.json()
    print(f"JSON Response: {json.dumps(json_response, indent=2)}")
except:
    print("Response is not valid JSON")