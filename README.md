# Candidate Filter API

A FastAPI backend for searching and filtering candidates from a CSV database.

## Features

- **Candidate Search**: Filter candidates by skills, experience, education, and more
- **Flexible Filtering**: Use any combination of search criteria
- **CSV Data Source**: Loads candidate data from CSV file
- **Comprehensive Validation**: Input validation with detailed error messages
- **Auto-generated Documentation**: Interactive Swagger UI
- **CORS Enabled**: Ready for frontend integration

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

## API Documentation

Once the server is running, you can access:
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## API Endpoints

### POST /search-candidates

Search for candidates based on filter criteria. Returns matching candidates from the CSV database.

**Request Body (all fields optional):**
```json
{
    "name": "John",
    "skills": ["java", "python"],
    "optionalSkills": ["react", "docker"],
    "instituteName": ["IIT", "MIT"],
    "course": ["Computer Science", "MCA"],
    "minExperience": 2,
    "maxExperience": 5,
    "phoneNumber": "+1-555",
    "email": "john@email.com",
    "companyName": ["google", "tcs"]
}
```

**Response:**
```json
{
    "total_candidates": 2,
    "candidates": [
        {
            "name": "John Doe",
            "skills": ["java", "python"],
            "optionalSkills": ["react", "angular"],
            "instituteName": "MIT",
            "course": "Computer Science",
            "minExperience": 2,
            "maxExperience": 5,
            "phoneNumber": "+1-555-0101",
            "email": "john@email.com",
            "companyName": ["google", "microsoft"]
        }
    ],
    "filter_applied": {
        "name": "John",
        "skills": ["java", "python"],
        "optionalSkills": ["react", "docker"],
        "instituteName": ["IIT", "MIT"],
        "course": ["Computer Science", "MCA"],
        "experience": {"min": 2, "max": 5},
        "phoneNumber": "+1-555",
        "email": "john@email.com",
        "companyName": ["google", "tcs"]
    }
}
```

### GET /all-candidates

Returns all candidates from the CSV database.

### GET /

Root endpoint - returns API status message.

### GET /health

Health check endpoint for monitoring.

## Sample Data

The API includes sample candidate data in `sample_candidates.csv` with 6 candidates from various backgrounds:
- Tech companies (Google, Microsoft, TCS, etc.)
- Educational institutions (MIT, Stanford, IIT)
- Various skills (Java, Python, JavaScript, React, etc.)

## Example Usage

### Search for Java developers:
```bash
curl -X POST "http://localhost:8000/search-candidates" \
     -H "Content-Type: application/json" \
     -d '{"skills": ["java"]}'
```

### Search by experience range:
```bash
curl -X POST "http://localhost:8000/search-candidates" \
     -H "Content-Type: application/json" \
     -d '{
       "minExperience": 2,
       "maxExperience": 5,
       "instituteName": ["IIT", "MIT"]
     }'
```

### Get all candidates:
```bash
curl -X GET "http://localhost:8000/all-candidates"
```

## Filtering Logic

- **Skills**: Candidate must have ALL specified skills (AND logic)
- **Optional Skills**: Candidate must have at least ONE specified skill (OR logic)
- **Experience**: Candidate's experience range must overlap with specified range
- **Institution/Course/Company**: Exact match (case-insensitive)
- **Name/Email**: Partial match (case-insensitive)
- **All filters are optional** - you can search by any combination

## Project Structure

```
├── main.py                 # FastAPI application
├── sample_candidates.csv   # Sample candidate data
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── quick_test.py          # Direct model testing
├── test_api.py            # API endpoint testing
└── test_validation.py     # Validation testing
```