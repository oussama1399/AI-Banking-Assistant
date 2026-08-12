"""
Test script to verify API endpoints are working correctly.
"""

import requests
import json

def test_api_endpoints():
    base_url = "http://localhost:8000"

    # Test root endpoint
    print("Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Root endpoint response: {response.json()}")

    # Test health endpoint
    print("\nTesting health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Health endpoint status: {response.status_code}")
    print(f"Health endpoint response: {response.json()}")

    # Test API v1 health endpoint
    print("\nTesting API v1 health endpoint...")
    response = requests.get(f"{base_url}/api/v1/health")
    print(f"API v1 Health endpoint status: {response.status_code}")
    print(f"API v1 Health endpoint response: {response.json()}")

    # Test chat endpoint with a simple request
    print("\nTesting chat endpoint...")
    payload = {
        "customer_id": "C1024",
        "message": "Quel est le statut de mon virement TR4587 ?"
    }

    response = requests.post(
        f"{base_url}/api/v1/chat",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    print(f"Chat endpoint status: {response.status_code}")
    if response.status_code == 200:
        print(f"Chat response: {response.json()}")
    else:
        print(f"Chat error: {response.text}")

if __name__ == "__main__":
    test_api_endpoints()