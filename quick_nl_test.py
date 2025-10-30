#!/usr/bin/env python3
"""
Quick test for natural language functionality without server
"""

from main import parse_natural_language_query, generate_query_interpretation, load_candidates_from_csv, filter_candidates


def test_end_to_end():
    print("End-to-End Natural Language Search Test")
    print("=" * 50)

    # Test queries
    queries = [
        "Show me candidates from IIT with java skills",
        "Find python developers with minimum 2 years experience",
        "Candidates from MIT or Stanford with react skills"
    ]

    # Load candidates
    all_candidates = load_candidates_from_csv()
    print(f"Loaded {len(all_candidates)} candidates from CSV")

    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: '{query}'")
        print("-" * 40)

        # Parse query
        filter_criteria = parse_natural_language_query(query)
        interpretation = generate_query_interpretation(query, filter_criteria)

        # Filter candidates
        matching_candidates = filter_candidates(
            all_candidates, filter_criteria)

        print(f"Parsed as: {interpretation}")
        print(f"Found {len(matching_candidates)} matching candidates:")

        for candidate in matching_candidates:
            print(
                f"  - {candidate.name} ({candidate.instituteName}) - Skills: {', '.join(candidate.skills)}")

        if len(matching_candidates) == 0:
            print("  (No matches found)")


if __name__ == "__main__":
    test_end_to_end()
