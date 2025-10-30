from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
import re
from datetime import datetime

app = FastAPI(title="Candidate Filter API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Pydantic models with comprehensive validation


class ExperienceRange(BaseModel):
    min: Optional[int] = Field(
        None, ge=0, le=50, description="Minimum years of experience")
    max: Optional[int] = Field(
        None, ge=0, le=50, description="Maximum years of experience")

    @validator('max')
    def validate_experience_range(cls, v, values):
        """Validate that max experience is greater than or equal to min experience"""
        if v is not None and 'min' in values and values['min'] is not None:
            if v < values['min']:
                raise ValueError(
                    'Maximum experience must be greater than or equal to minimum experience')
        return v


class CandidateFilter(BaseModel):
    """Enhanced response model with proper defaults and validation"""
    name: str = Field(default="", description="Candidate name")
    skills: List[str] = Field(default_factory=list,
                              description="Required technical skills")
    optionalSkills: List[str] = Field(
        default_factory=list, description="Optional technical skills")
    instituteName: List[str] = Field(
        default_factory=list, description="Educational institution names")
    course: List[str] = Field(default_factory=list, description="Course names")
    experience: ExperienceRange = Field(
        default_factory=ExperienceRange, description="Experience range")
    phoneNumber: str = Field(default="", description="Contact phone number")
    email: str = Field(default="", description="Contact email address")
    companyName: List[str] = Field(
        default_factory=list, description="Company names")


class CandidateFilterRequest(BaseModel):
    """Enhanced request model with comprehensive validation"""
    name: Optional[str] = Field(
        None, max_length=100, description="Candidate name")
    skills: Optional[List[str]] = Field(
        None, description="Required technical skills")
    optionalSkills: Optional[List[str]] = Field(
        None, description="Optional technical skills")
    instituteName: Optional[List[str]] = Field(
        None, description="Educational institution names")
    course: Optional[List[str]] = Field(None, description="Course names")
    minExperience: Optional[int] = Field(
        None, ge=0, le=50, description="Minimum years of experience")
    maxExperience: Optional[int] = Field(
        None, ge=0, le=50, description="Maximum years of experience")
    phoneNumber: Optional[str] = Field(
        None, max_length=20, description="Contact phone number")
    email: Optional[str] = Field(
        None, max_length=254, description="Contact email address")
    companyName: Optional[List[str]] = Field(None, description="Company names")

    @validator('email')
    def validate_email_format(cls, v):
        """Validate email format using regex"""
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
        return v.strip() if v else v

    @validator('phoneNumber')
    def validate_phone_format(cls, v):
        """Validate phone number format"""
        if v is not None and v.strip():
            # Allow international format with optional + and various separators
            phone_pattern = r'^\+?[\d\s\-\(\)]{7,20}$'
            cleaned_phone = re.sub(r'[\s\-\(\)]', '', v.strip())
            if not re.match(phone_pattern, v.strip()) or len(cleaned_phone) < 7:
                raise ValueError(
                    'Invalid phone number format. Use international format with 7-20 digits')
        return v.strip() if v else v

    @validator('maxExperience')
    def validate_experience_range(cls, v, values):
        """Validate that max experience is greater than or equal to min experience"""
        if v is not None and 'minExperience' in values and values['minExperience'] is not None:
            if v < values['minExperience']:
                raise ValueError(
                    'Maximum experience must be greater than or equal to minimum experience')
        return v

    @validator('skills', 'optionalSkills', 'instituteName', 'course', 'companyName')
    def validate_string_arrays(cls, v):
        """Validate and clean string arrays"""
        if v is not None:
            # Filter out empty strings and strip whitespace
            cleaned = [item.strip() for item in v if item and item.strip()]
            # Remove duplicates while preserving order
            seen = set()
            result = []
            for item in cleaned:
                if item.lower() not in seen:
                    seen.add(item.lower())
                    result.append(item)
            return result
        return v

    @validator('name')
    def validate_name(cls, v):
        """Validate and clean name field"""
        if v is not None:
            return v.strip()
        return v


class APIResponse(BaseModel):
    """Standardized API response model for consistent error handling"""
    success: bool = Field(
        description="Indicates if the request was successful")
    data: Optional[CandidateFilter] = Field(
        None, description="Response data when successful")
    message: str = Field(description="Human-readable message")
    errors: Optional[List[str]] = Field(
        None, description="List of error messages when unsuccessful")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(
        None, description="Unique request identifier for tracking")


@app.get("/")
async def root():
    return {"message": "Candidate Filter API is running"}


@app.post("/filter-candidate", response_model=CandidateFilter)
async def filter_candidate(request: CandidateFilterRequest):
    """
    Endpoint to create a candidate filter object.
    Users can provide any subset of the fields, and the response will be formatted
    according to the specified structure.
    """

    # Create experience object
    experience = ExperienceRange()
    if request.minExperience is not None:
        experience.min = request.minExperience
    if request.maxExperience is not None:
        experience.max = request.maxExperience

    # Create the filter response
    candidate_filter = CandidateFilter(
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

    return candidate_filter


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
