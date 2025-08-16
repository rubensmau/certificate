#!/usr/bin/env python3
"""
Simple test script for the token API
Run with: python test_api.py
"""
import requests
import json

BASE_URL = "https://certificate-q4q0.onrender.com/"  # "http://localhost:5000"


def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()


def test_store_certificate():
    """Test certificate storage"""
    print("Testing certificate storage...")
    test_data = {
        "token": "test-token-123",
        "de": "João Silva",
        "para": "Instituto Beneficente"
    }
    response = requests.post(f"{BASE_URL}/certificate", json=test_data)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    print()
    return test_data["token"]


def test_list_tokens():
    """Test listing all tokens"""
    print("Testing token listing...")
    response = requests.get(f"{BASE_URL}/tokens")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Number of tokens: {len(data.get('tokens', []))}")
    print()


def main():
    """Run all tests"""
    print("=== Certificate API Test Suite ===\n")

    # Test health
    test_health()

    # Store a certificate
    token = test_store_certificate()

    # List all tokens
    test_list_tokens()

    print("=== Tests completed ===")


if __name__ == "__main__":
    main()
