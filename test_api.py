#!/usr/bin/env python3
"""
Test script to demonstrate the API filtering capabilities
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_api_filtering():
    print("Testing Candidate Filter API")
    print("=" * 50)

    # Test cases demonstrating different filtering scenarios
    test_cases = [
        {
            "name": "Test 1: Single skill filter",
            "data": {
                "skills": ["java"]
            }
        },
        {
            "name": "Test 2: Multiple skills filter",
            "data": {
                "skills": ["java", "python"],
                "optionalSkills": ["react"]
            }
        },
        {
            "name": "Test 3: Experience range only",
            "data": {
                "minExperience": 2,
                "maxExperience": 5
            }
        },
        {
            "name": "Test 4: Institution and course filter",
            "data": {
                "instituteName": ["IIT", "MIT"],
                "course": ["Computer Science"]
            }
        },
        {
            "name": "Test 5: Company filter",
            "data": {
                "companyName": ["tcs", "google"]
            }
        },
        {
            "name": "Test 6: Complete filter",
            "data": {
                "name": "John",
                "skills": ["java"],
                "optionalSkills": ["react", "angular"],
                "instituteName": ["MIT"],
                "course": ["Computer Science"],
                "minExperience": 2,
                "maxExperience": 5,
                "email": "john@email.com",
                "companyName": ["google"]
            }
        },
        {
            "name": "Test 7: Empty filter (all defaults)",
            "data": {}
        },
        {
            "name": "Test 8: Only optional skills",
            "data": {
                "optionalSkills": ["docker", "kubernetes"]
            }
        }
    ]

    for test_case in test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Request: {json.dumps(test_case['data'], indent=2)}")

        try:
            response = requests.post(
                f"{BASE_URL}/filter-candidate", json=test_case['data'])

            if response.status_code == 200:
                result = response.json()
                print("✓ Success!")
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"✗ Error: {response.status_code}")
                print(f"Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print(
                "✗ Connection Error: Make sure the API server is running on localhost:8000")
            print("  Run: python main.py")
            break
        except Exception as e:
            print(f"✗ Error: {e}")

        print("-" * 30)


def test_validation_errors():
    print("\n\nTesting Validation Errors")
    print("=" * 50)

    error_test_cases = [
        {
            "name": "Invalid email format",
            "data": {"email": "invalid-email"}
        },
        {
            "name": "Invalid phone number",
            "data": {"phoneNumber": "123"}
        },
        {
            "name": "Invalid experience range",
            "data": {"minExperience": 10, "maxExperience": 5}
        },
        {
            "name": "Negative experience",
            "data": {"minExperience": -1}
        }
    ]

    for test_case in error_test_cases:
        print(f"\n{test_case['name']}:")
        print(f"Request: {json.dumps(test_case['data'], indent=2)}")

        try:
            response = requests.post(
                f"{BASE_URL}/filter-candidate", json=test_case['data'])

            if response.status_code == 422:
                print("✓ Validation error correctly caught!")
                error_detail = response.json()
                print(f"Error: {json.dumps(error_detail, indent=2)}")
            else:
                print(
                    f"✗ Expected validation error, got: {response.status_code}")
                print(f"Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print("✗ Connection Error: Make sure the API server is running")
            break
        except Exception as e:
            print(f"✗ Error: {e}")


if __name__ == "__main__":
    print("Make sure to start the API server first:")
    print("python main.py")
    print("\nThen run this test script in another terminal")
    print("=" * 50)

    test_api_filtering()
    test_validation_errors()
