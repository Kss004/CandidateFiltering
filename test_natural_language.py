#!/usr/bin/env python3
"""
Test script for natural language search functionality
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"


def test_natural_language_search():
    print("Testing Natural Language Search API")
    print("=" * 60)

    # Test cases with natural language queries
    test_queries = [
        "Show me candidates from IIT or MIT with minimum 2 years of experience in java",
        "Find python developers with 3-5 years experience",
        "Candidates with react and nodejs skills from Google or Microsoft",
        "Show me developers from Stanford with machine learning experience",
        "Find candidates with java and spring skills from TCS",
        "Python developers from IIT with minimum 3 years experience",
        "Show me candidates with docker and kubernetes skills",
        "Find javascript developers with 1-4 years experience from startups",
        "Candidates from MIT or Stanford with computer science degree",
        "Show me developers with tensorflow and pytorch skills",
        "Find candidates with microservices experience from Netflix or Uber",
        "Python or java developers with minimum 2 years experience"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 50)

        try:
            response = requests.post(
                f"{BASE_URL}/natural-language-search",
                json={"query": query}
            )

            if response.status_code == 200:
                result = response.json()
                print("✓ Success!")
                print(f"Parsed as: {result['parsed_query']}")
                print(f"Found {result['total_candidates']} candidates:")

                for candidate in result['candidates']:
                    print(
                        f"  - {candidate['name']} ({candidate['instituteName']}) - Skills: {', '.join(candidate['skills'])}")

                if result['total_candidates'] == 0:
                    print("  (No matching candidates found)")

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

        print()


def test_direct_parsing():
    """Test the parsing logic directly without API calls"""
    print("\n" + "=" * 60)
    print("Testing Direct Query Parsing (No Server Required)")
    print("=" * 60)

    # Import the parsing function
    try:
        from main import parse_natural_language_query, generate_query_interpretation

        test_queries = [
            "Show me candidates from IIT with java skills and minimum 2 years experience",
            "Find python developers from Google or Microsoft",
            "Candidates with react skills from MIT or Stanford",
            "Show me developers with 3-5 years experience in machine learning"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 40)

            try:
                filter_criteria = parse_natural_language_query(query)
                interpretation = generate_query_interpretation(
                    query, filter_criteria)

                print(f"Parsed as: {interpretation}")
                print("Filter criteria:")

                if filter_criteria.skills:
                    print(f"  Skills: {filter_criteria.skills}")
                if filter_criteria.optionalSkills:
                    print(
                        f"  Optional Skills: {filter_criteria.optionalSkills}")
                if filter_criteria.instituteName:
                    print(f"  Institutions: {filter_criteria.instituteName}")
                if filter_criteria.companyName:
                    print(f"  Companies: {filter_criteria.companyName}")
                if filter_criteria.minExperience:
                    print(f"  Min Experience: {filter_criteria.minExperience}")
                if filter_criteria.maxExperience:
                    print(f"  Max Experience: {filter_criteria.maxExperience}")

            except Exception as e:
                print(f"✗ Parsing Error: {e}")

    except ImportError:
        print("Could not import parsing functions. Make sure main.py is in the same directory.")


if __name__ == "__main__":
    print("Natural Language Search Testing")
    print("Make sure to start the API server first: python main.py")
    print("Then run this test script")
    print()

    # Test direct parsing first (doesn't require server)
    test_direct_parsing()

    # Test API endpoints (requires server)
    test_natural_language_search()
