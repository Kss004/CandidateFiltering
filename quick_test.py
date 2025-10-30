#!/usr/bin/env python3
"""
Quick test without needing to run the server - just test the models directly
"""

from main import CandidateFilter, CandidateFilterRequest, ExperienceRange
import json


def test_filtering_scenarios():
    print("Testing Candidate Filter Scenarios (Direct Model Testing)")
    print("=" * 60)

    scenarios = [
        {
            "name": "Single skill only",
            "input": {"skills": ["java"]}
        },
        {
            "name": "Multiple skills",
            "input": {"skills": ["java", "python"], "optionalSkills": ["react"]}
        },
        {
            "name": "Experience range only",
            "input": {"minExperience": 2, "maxExperience": 5}
        },
        {
            "name": "Institution filter",
            "input": {"instituteName": ["IIT"], "course": ["MCA"]}
        },
        {
            "name": "Company filter",
            "input": {"companyName": ["tcs", "infosys"]}
        },
        {
            "name": "Complete filter",
            "input": {
                "name": "John Doe",
                "skills": ["java"],
                "optionalSkills": ["spring", "microservices"],
                "instituteName": ["IIT"],
                "course": ["Computer Science"],
                "minExperience": 2,
                "maxExperience": 5,
                "phoneNumber": "+1-555-0101",
                "email": "john@email.com",
                "companyName": ["google", "microsoft"]
            }
        },
        {
            "name": "Empty filter (all defaults)",
            "input": {}
        },
        {
            "name": "Only optional skills",
            "input": {"optionalSkills": ["docker", "kubernetes"]}
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print(f"Input: {json.dumps(scenario['input'], indent=2)}")

        try:
            # Create request object
            request = CandidateFilterRequest(**scenario['input'])

            # Create experience object
            experience = ExperienceRange()
            if hasattr(request, 'minExperience') and request.minExperience is not None:
                experience.min = request.minExperience
            if hasattr(request, 'maxExperience') and request.maxExperience is not None:
                experience.max = request.maxExperience

            # Create filter response
            filter_result = CandidateFilter(
                name=request.name or "",
                skills=request.skills or [],
                optionalSkills=request.optionalSkills or [],
                instituteName=request.instituteName or [],
                course=request.course or [],
                experience=experience,
                phoneNumber=request.phoneNumber or "",
                email=request.email or "",
                companyName=request.companyName or []
            )

            print("✓ Success!")
            print(
                f"Output: {json.dumps(filter_result.model_dump(), indent=2)}")

        except Exception as e:
            print(f"✗ Error: {e}")

        print("-" * 40)


if __name__ == "__main__":
    test_filtering_scenarios()
