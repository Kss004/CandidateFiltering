# Candidate Filter API

A simple FastAPI backend for candidate filtering that returns structured candidate filter data.

## Features

- RESTful API endpoint for candidate filtering
- Flexible input - users can provide any subset of fields
- Structured output format with consistent schema
- No LLM integration - purely functional and minimalistic
- CORS enabled for frontend integration

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

### POST /filter-candidate

Creates a candidate filter object based on the provided criteria.

**Request Body (all fields optional):**
```json
{
    "name": "string",
    "skills": ["java", "python"],
    "optionalSkills": ["javascript", "react"],
    "instituteName": ["IIT", "NIT"],
    "course": ["MCA", "B.Tech"],
    "minExperience": 1,
    "maxExperience": 12,
    "phoneNumber": "string",
    "email": "string",
    "companyName": ["tcs", "infosys"]
}
```

**Response:**
```json
{
    "name": "",
    "skills": ["java"],
    "optionalSkills": ["javascript"],
    "instituteName": ["IIT"],
    "course": ["MCA"],
    "experience": {
        "min": 1,
        "max": 12
    },
    "phoneNumber": "",
    "email": "",
    "companyName": ["tcs"]
}
```

### GET /

Health check endpoint that returns a welcome message.

### GET /health

Returns the health status of the API.

## Example Usage

```bash
curl -X POST "http://localhost:8000/filter-candidate" \
     -H "Content-Type: application/json" \
     -d '{
       "skills": ["java", "python"],
       "instituteName": ["IIT"],
       "minExperience": 2,
       "maxExperience": 5
     }'
```

## Notes

- All fields are optional in the request
- Empty fields will be returned as empty strings or empty arrays in the response
- Experience is handled as separate min/max fields in the request but returned as an object
- The API maintains the exact output format as specified in the requirements