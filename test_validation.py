#!/usr/bin/env python3
"""
Test script to verify the enhanced model validation
"""

from main import CandidateFilterRequest, ExperienceRange, CandidateFilter, APIResponse
from pydantic import ValidationError
import json


def test_validation():
    print("Testing Enhanced Model Validation")
    print("=" * 50)

    # Test 1: Valid request with all validations
    print("\n1. Testing valid request:")
    try:
        valid_req = CandidateFilterRequest(
            name="  John Doe  ",  # Test name trimming
            email="john@example.com",
            phoneNumber="+1-234-567-8900",
            minExperience=2,
            maxExperience=5,
            # Test deduplication and empty removal
            skills=["python", "java", "", "Python"],
            optionalSkills=["react", "vue"]
        )
        print("✓ Valid request created successfully")
        print(f"  Cleaned name: '{valid_req.name}'")
        print(f"  Cleaned skills: {valid_req.skills}")
    except ValidationError as e:
        print(f"✗ Valid request failed: {e}")

    # Test 2: Invalid email format
    print("\n2. Testing invalid email:")
    try:
        invalid_email = CandidateFilterRequest(email="invalid-email")
        print("✗ Invalid email test failed - should have raised error")
    except ValidationError as e:
        print("✓ Invalid email correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    # Test 3: Invalid phone number
    print("\n3. Testing invalid phone number:")
    try:
        invalid_phone = CandidateFilterRequest(phoneNumber="123")
        print("✗ Invalid phone test failed - should have raised error")
    except ValidationError as e:
        print("✓ Invalid phone correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    # Test 4: Invalid experience range in request
    print("\n4. Testing invalid experience range in request:")
    try:
        invalid_exp = CandidateFilterRequest(minExperience=10, maxExperience=5)
        print("✗ Invalid experience test failed - should have raised error")
    except ValidationError as e:
        print("✓ Invalid experience range correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    # Test 5: Invalid experience range in ExperienceRange model
    print("\n5. Testing invalid ExperienceRange model:")
    try:
        exp_range = ExperienceRange(min=10, max=5)
        print("✗ Invalid ExperienceRange test failed - should have raised error")
    except ValidationError as e:
        print("✓ Invalid ExperienceRange correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    # Test 6: Experience bounds validation
    print("\n6. Testing experience bounds:")
    try:
        invalid_bounds = CandidateFilterRequest(minExperience=-1)
        print("✗ Negative experience test failed - should have raised error")
    except ValidationError as e:
        print("✓ Negative experience correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    try:
        invalid_bounds = CandidateFilterRequest(maxExperience=100)
        print("✗ Excessive experience test failed - should have raised error")
    except ValidationError as e:
        print("✓ Excessive experience correctly rejected")
        print(f"  Error: {e.errors()[0]['msg']}")

    # Test 7: CandidateFilter response model
    print("\n7. Testing CandidateFilter response model:")
    try:
        filter_response = CandidateFilter(
            name="John Doe",
            skills=["python", "java"],
            experience=ExperienceRange(min=2, max=5)
        )
        print("✓ CandidateFilter created successfully")
        print(
            f"  Default values: email='{filter_response.email}', phoneNumber='{filter_response.phoneNumber}'")
    except Exception as e:
        print(f"✗ CandidateFilter creation failed: {e}")

    # Test 8: APIResponse model
    print("\n8. Testing APIResponse model:")
    try:
        api_response = APIResponse(
            success=True,
            message="Request processed successfully",
            data=CandidateFilter(name="Test")
        )
        print("✓ APIResponse created successfully")
        print(f"  Timestamp: {api_response.timestamp}")
    except Exception as e:
        print(f"✗ APIResponse creation failed: {e}")


if __name__ == "__main__":
    test_validation()
