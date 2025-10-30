from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
import re
from datetime import datetime
import pandas as pd
import os

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


class Candidate(BaseModel):
    """Model representing a candidate from the CSV data"""
    name: str
    skills: List[str]
    optionalSkills: List[str]
    instituteName: str
    course: str
    minExperience: int
    maxExperience: int
    phoneNumber: str
    email: str
    companyName: List[str]


class CandidateSearchResponse(BaseModel):
    """Response model for candidate search results"""
    total_candidates: int = Field(
        description="Total number of matching candidates")
    candidates: List[Candidate] = Field(
        description="List of matching candidates")
    filter_applied: CandidateFilter = Field(
        description="Filter criteria that was applied")


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


class NaturalLanguageRequest(BaseModel):
    """Request model for natural language search"""
    query: str = Field(description="Natural language search query")


class NaturalLanguageResponse(BaseModel):
    """Response model for natural language search results"""
    total_candidates: int = Field(
        description="Total number of matching candidates")
    candidates: List[Candidate] = Field(
        description="List of matching candidates")
    parsed_query: str = Field(description="How the query was interpreted")
    filter_applied: CandidateFilter = Field(
        description="Filter criteria that was extracted")


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


def parse_natural_language_query(query: str) -> CandidateFilterRequest:
    """
    Parse natural language query into structured filter criteria.
    Simple NLP parser using regex patterns and keyword matching.
    """
    query_lower = query.lower().strip()

    # Initialize filter criteria
    filter_criteria = CandidateFilterRequest()

    # Parse institutions (IIT, MIT, Stanford, etc.)
    institution_patterns = [
        r'\b(iit|indian institute of technology)\b',
        r'\b(mit|massachusetts institute of technology)\b',
        r'\bstanford\b',
        r'\bharvard\b',
        r'\bcaltech\b',
        r'\bnit\b'
    ]

    institutions = []
    for pattern in institution_patterns:
        matches = re.findall(pattern, query_lower)
        for match in matches:
            if 'iit' in match or 'indian institute' in match:
                institutions.append('IIT')
            elif 'mit' in match or 'massachusetts' in match:
                institutions.append('MIT')
            elif 'stanford' in match:
                institutions.append('Stanford')
            elif 'harvard' in match:
                institutions.append('Harvard')
            elif 'caltech' in match:
                institutions.append('Caltech')
            elif 'nit' in match:
                institutions.append('NIT')

    if institutions:
        filter_criteria.instituteName = list(
            set(institutions))  # Remove duplicates

    # Parse skills (java, python, javascript, etc.)
    skill_patterns = {
        r'\bjava\b(?!\s*script)': 'java',
        r'\bpython\b': 'python',
        r'\bjavascript\b|\bjs\b': 'javascript',
        r'\breact\b': 'react',
        r'\bangular\b': 'angular',
        r'\bvue\b': 'vue',
        r'\bnode\.?js\b': 'nodejs',
        r'\bspring\b': 'spring',
        r'\bdjango\b': 'django',
        r'\bdocker\b': 'docker',
        r'\bkubernetes\b|\bk8s\b': 'kubernetes',
        r'\baws\b': 'aws',
        r'\bmachine learning\b|\bml\b': 'machine learning',
        r'\btensorflow\b': 'tensorflow',
        r'\bpytorch\b': 'pytorch',
        r'\bmicroservices\b': 'microservices',
        r'\bredis\b': 'redis',
        r'\btypescript\b': 'typescript',
        r'\bgraphql\b': 'graphql'
    }

    skills = []
    optional_skills = []

    for pattern, skill in skill_patterns.items():
        if re.search(pattern, query_lower):
            # Check if it's mentioned as optional/nice-to-have
            skill_context = re.search(
                rf'.{{0,20}}{pattern}.{{0,20}}', query_lower)
            if skill_context:
                context = skill_context.group()
                if any(word in context for word in ['optional', 'nice', 'good to have', 'plus', 'bonus']):
                    optional_skills.append(skill)
                else:
                    skills.append(skill)

    if skills:
        filter_criteria.skills = skills
    if optional_skills:
        filter_criteria.optionalSkills = optional_skills

    # Parse experience (minimum/maximum years)
    exp_patterns = [
        r'(?:minimum|min|at least|more than)\s+(\d+)\s+years?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s+years?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(?:minimum|min|at least)\s+(\d+)\s+years?',
        r'with\s+(\d+)\+?\s+years?\s+(?:of\s+)?experience'
    ]

    for pattern in exp_patterns:
        match = re.search(pattern, query_lower)
        if match:
            min_exp = int(match.group(1))
            filter_criteria.minExperience = min_exp
            break

    # Parse maximum experience
    max_exp_patterns = [
        r'(?:maximum|max|up to|less than)\s+(\d+)\s+years?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(?:maximum|max|up to)\s+(\d+)\s+years?'
    ]

    for pattern in max_exp_patterns:
        match = re.search(pattern, query_lower)
        if match:
            max_exp = int(match.group(1))
            filter_criteria.maxExperience = max_exp
            break

    # Parse experience range (e.g., "2-5 years experience")
    range_pattern = r'(\d+)\s*[-–]\s*(\d+)\s+years?\s+(?:of\s+)?experience'
    range_match = re.search(range_pattern, query_lower)
    if range_match:
        filter_criteria.minExperience = int(range_match.group(1))
        filter_criteria.maxExperience = int(range_match.group(2))

    # Parse companies
    company_patterns = {
        r'\bgoogle\b': 'google',
        r'\bmicrosoft\b|\bmsft\b': 'microsoft',
        r'\bfacebook\b|\bmeta\b': 'facebook',
        r'\bamazon\b': 'amazon',
        r'\btcs\b': 'tcs',
        r'\binfosys\b': 'infosys',
        r'\bwipro\b': 'wipro',
        r'\bcognizant\b': 'cognizant',
        r'\bnetflix\b': 'netflix',
        r'\buber\b': 'uber',
        r'\bstartup\b': 'startup'
    }

    companies = []
    for pattern, company in company_patterns.items():
        if re.search(pattern, query_lower):
            companies.append(company)

    if companies:
        filter_criteria.companyName = companies

    # Parse courses
    course_patterns = {
        r'\bcomputer science\b|\bcs\b': 'Computer Science',
        r'\bmca\b': 'MCA',
        r'\bb\.?tech\b|\bbachelor of technology\b': 'B.Tech',
        r'\bm\.?tech\b|\bmaster of technology\b': 'M.Tech',
        r'\bsoftware engineering\b': 'Software Engineering',
        r'\binformation technology\b|\bit\b': 'Information Technology',
        r'\bdata science\b': 'Data Science'
    }

    courses = []
    for pattern, course in course_patterns.items():
        if re.search(pattern, query_lower):
            courses.append(course)

    if courses:
        filter_criteria.course = courses

    # Parse names (if mentioned) - be more specific to avoid false positives
    name_patterns = [
        r'(?:named?|called)\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)',
        r'candidate\s+([a-zA-Z]+(?:\s+[a-zA-Z]+)?)(?!\s+(?:with|from|who))'
    ]

    for pattern in name_patterns:
        match = re.search(pattern, query_lower)
        if match:
            name = match.group(1).strip()
            # Avoid common words and technical terms
            excluded_words = [
                'with', 'from', 'who', 'that', 'have', 'has', 'experience', 'years',
                'developers', 'developer', 'candidates', 'candidate', 'skills', 'skill',
                'python', 'java', 'javascript', 'react', 'angular', 'vue', 'nodejs'
            ]
            if name.lower() not in excluded_words and not any(word in name.lower() for word in excluded_words):
                filter_criteria.name = name.title()
                break

    return filter_criteria


def generate_query_interpretation(query: str, filter_criteria: CandidateFilterRequest) -> str:
    """Generate a human-readable interpretation of what was parsed from the query"""
    interpretations = []

    if filter_criteria.name:
        interpretations.append(f"Name contains '{filter_criteria.name}'")

    if filter_criteria.skills:
        interpretations.append(
            f"Must have skills: {', '.join(filter_criteria.skills)}")

    if filter_criteria.optionalSkills:
        interpretations.append(
            f"Nice to have skills: {', '.join(filter_criteria.optionalSkills)}")

    if filter_criteria.instituteName:
        interpretations.append(
            f"From institutions: {', '.join(filter_criteria.instituteName)}")

    if filter_criteria.course:
        interpretations.append(f"Course: {', '.join(filter_criteria.course)}")

    if filter_criteria.minExperience is not None:
        interpretations.append(
            f"Minimum {filter_criteria.minExperience} years experience")

    if filter_criteria.maxExperience is not None:
        interpretations.append(
            f"Maximum {filter_criteria.maxExperience} years experience")

    if filter_criteria.companyName:
        interpretations.append(
            f"From companies: {', '.join(filter_criteria.companyName)}")

    if not interpretations:
        return "No specific criteria found - showing all candidates"

    return "; ".join(interpretations)


@app.get("/")
async def root():
    return {"message": "Candidate Filter API is running"}


def load_candidates_from_csv():
    """Load candidates from CSV file"""
    csv_file = "sample_candidates.csv"
    if not os.path.exists(csv_file):
        return []

    try:
        df = pd.read_csv(csv_file)
        candidates = []

        for _, row in df.iterrows():
            # Parse comma-separated skills
            skills = [skill.strip() for skill in str(
                row['skills']).split(',') if skill.strip()]
            optional_skills = [skill.strip() for skill in str(
                row['optionalSkills']).split(',') if skill.strip()]
            company_names = [company.strip() for company in str(
                row['companyName']).split(',') if company.strip()]

            candidate = Candidate(
                name=str(row['name']),
                skills=skills,
                optionalSkills=optional_skills,
                instituteName=str(row['instituteName']),
                course=str(row['course']),
                minExperience=int(row['minExperience']),
                maxExperience=int(row['maxExperience']),
                phoneNumber=str(row['phoneNumber']),
                email=str(row['email']),
                companyName=company_names
            )
            candidates.append(candidate)

        return candidates
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def filter_candidates(candidates: List[Candidate], filter_criteria: CandidateFilterRequest) -> List[Candidate]:
    """Filter candidates based on the provided criteria"""
    filtered = []

    for candidate in candidates:
        match = True

        # Name filter (partial match, case insensitive)
        if filter_criteria.name and filter_criteria.name.strip():
            if filter_criteria.name.lower() not in candidate.name.lower():
                match = False
                continue

        # Skills filter (candidate must have ALL required skills)
        if filter_criteria.skills:
            candidate_skills_lower = [skill.lower()
                                      for skill in candidate.skills]
            for required_skill in filter_criteria.skills:
                if required_skill.lower() not in candidate_skills_lower:
                    match = False
                    break
            if not match:
                continue

        # Optional skills filter (candidate should have at least one)
        if filter_criteria.optionalSkills:
            candidate_all_skills = [
                skill.lower() for skill in candidate.skills + candidate.optionalSkills]
            has_optional_skill = any(opt_skill.lower() in candidate_all_skills
                                     for opt_skill in filter_criteria.optionalSkills)
            if not has_optional_skill:
                match = False
                continue

        # Institution filter
        if filter_criteria.instituteName:
            if candidate.instituteName.lower() not in [inst.lower() for inst in filter_criteria.instituteName]:
                match = False
                continue

        # Course filter
        if filter_criteria.course:
            if candidate.course.lower() not in [course.lower() for course in filter_criteria.course]:
                match = False
                continue

        # Experience filter
        if filter_criteria.minExperience is not None:
            if candidate.maxExperience < filter_criteria.minExperience:
                match = False
                continue

        if filter_criteria.maxExperience is not None:
            if candidate.minExperience > filter_criteria.maxExperience:
                match = False
                continue

        # Email filter (partial match)
        if filter_criteria.email and filter_criteria.email.strip():
            if filter_criteria.email.lower() not in candidate.email.lower():
                match = False
                continue

        # Company filter
        if filter_criteria.companyName:
            candidate_companies_lower = [
                company.lower() for company in candidate.companyName]
            has_company = any(company.lower() in candidate_companies_lower
                              for company in filter_criteria.companyName)
            if not has_company:
                match = False
                continue

        if match:
            filtered.append(candidate)

    return filtered


@app.post("/search-candidates", response_model=CandidateSearchResponse)
async def search_candidates(request: CandidateFilterRequest):
    """
    Search for candidates based on filter criteria.
    Returns matching candidates from the CSV data.
    """
    # Load candidates from CSV
    all_candidates = load_candidates_from_csv()

    # Filter candidates based on criteria
    matching_candidates = filter_candidates(all_candidates, request)

    # Create the filter object for response
    experience = ExperienceRange()
    if request.minExperience is not None:
        experience.min = request.minExperience
    if request.maxExperience is not None:
        experience.max = request.maxExperience

    filter_applied = CandidateFilter(
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

    return CandidateSearchResponse(
        total_candidates=len(matching_candidates),
        candidates=matching_candidates,
        filter_applied=filter_applied
    )


@app.post("/natural-language-search", response_model=NaturalLanguageResponse)
async def natural_language_search(request: NaturalLanguageRequest):
    """
    Search for candidates using natural language queries.

    Examples:
    - "Show me candidates from IIT or MIT with minimum 2 years of experience in java"
    - "Find python developers with 3-5 years experience from Google or Microsoft"
    - "Candidates with react and nodejs skills from Stanford"
    """
    # Parse the natural language query
    filter_criteria = parse_natural_language_query(request.query)

    # Load candidates from CSV
    all_candidates = load_candidates_from_csv()

    # Filter candidates based on parsed criteria
    matching_candidates = filter_candidates(all_candidates, filter_criteria)

    # Generate interpretation
    interpretation = generate_query_interpretation(
        request.query, filter_criteria)

    # Create the filter object for response
    experience = ExperienceRange()
    if filter_criteria.minExperience is not None:
        experience.min = filter_criteria.minExperience
    if filter_criteria.maxExperience is not None:
        experience.max = filter_criteria.maxExperience

    filter_applied = CandidateFilter(
        name=filter_criteria.name or "",
        skills=filter_criteria.skills or [],
        optionalSkills=filter_criteria.optionalSkills or [],
        instituteName=filter_criteria.instituteName or [],
        course=filter_criteria.course or [],
        experience=experience,
        phoneNumber=filter_criteria.phoneNumber or "",
        email=filter_criteria.email or "",
        companyName=filter_criteria.companyName or []
    )

    return NaturalLanguageResponse(
        total_candidates=len(matching_candidates),
        candidates=matching_candidates,
        parsed_query=interpretation,
        filter_applied=filter_applied
    )


@app.get("/all-candidates", response_model=List[Candidate])
async def get_all_candidates():
    """Get all candidates from the CSV file"""
    return load_candidates_from_csv()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
