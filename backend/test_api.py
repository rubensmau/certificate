#!/usr/bin/env python3
"""
Simple test script for the token API
Run with: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_token():
    """Test token creation"""
    print("Testing token creation...")
    response = requests.post(f"{BASE_URL}/tokens")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")
    token = data.get('token')
    print(f"Generated token: {token}")
    print()
    return token

def test_validate_token(token):
    """Test token validation"""
    print(f"Testing token validation for: {token}")
    response = requests.get(f"{BASE_URL}/tokens/{token}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_complete_token(token):
    """Test token completion"""
    print(f"Testing token completion for: {token}")
    response = requests.delete(f"{BASE_URL}/tokens/{token}")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

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
    print("=== Token API Test Suite ===\n")
    
    # Test health
    test_health()
    
    # Create a token
    token = test_create_token()
    
    # Validate the token
    test_validate_token(token)
    
    # Try validating again (should still work, status IN_USE)
    test_validate_token(token)
    
    # Complete the token
    test_complete_token(token)
    
    # Try validating completed token (should fail)
    test_validate_token(token)
    
    # List all tokens
    test_list_tokens()
    
    print("=== Tests completed ===")

if __name__ == "__main__":
    main()