#!/usr/bin/env python3
"""
Simple test script to demonstrate the Candidate Filter API functionality.
Run this after starting the FastAPI server.
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_api():
    """Test the candidate filter API with various scenarios."""

    print("Testing Candidate Filter API")
    print("=" * 50)

    # Test 1: Full request with all fields
    print("\n1. Testing with all fields:")
    full_request = {
        "name": "John Doe",
        "skills": ["java", "python", "sql"],
        "optionalSkills": ["javascript", "react"],
        "instituteName": ["IIT Delhi", "IIT Mumbai"],
        "course": ["MCA", "B.Tech"],
        "minExperience": 2,
        "maxExperience": 8,
        "phoneNumber": "+91-9876543210",
        "email": "john.doe@example.com",
        "companyName": ["tcs", "infosys", "wipro"]
    }

    try:
        response = requests.post(
            f"{BASE_URL}/filter-candidate", json=full_request)
        response.raise_for_status()
        print("Request:", json.dumps(full_request, indent=2))
        print("Response:", json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Test 2: Partial request (only skills and experience)
    print("\n2. Testing with partial fields (skills and experience only):")
    partial_request = {
        "skills": ["java"],
        "minExperience": 1,
        "maxExperience": 5
    }

    try:
        response = requests.post(
            f"{BASE_URL}/filter-candidate", json=partial_request)
        response.raise_for_status()
        print("Request:", json.dumps(partial_request, indent=2))
        print("Response:", json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Test 3: Empty request
    print("\n3. Testing with empty request:")
    empty_request = {}

    try:
        response = requests.post(
            f"{BASE_URL}/filter-candidate", json=empty_request)
        response.raise_for_status()
        print("Request:", json.dumps(empty_request, indent=2))
        print("Response:", json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    # Test 4: Only experience min
    print("\n4. Testing with only minimum experience:")
    min_exp_request = {
        "minExperience": 3
    }

    try:
        response = requests.post(
            f"{BASE_URL}/filter-candidate", json=min_exp_request)
        response.raise_for_status()
        print("Request:", json.dumps(min_exp_request, indent=2))
        print("Response:", json.dumps(response.json(), indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print(f"Server is running at {BASE_URL}")
        test_api()
    except requests.exceptions.RequestException:
        print(f"Error: Server is not running at {BASE_URL}")
        print("Please start the FastAPI server first by running: python main.py")
