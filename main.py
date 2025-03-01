from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import requests
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# External API configurations (Replace with actual API keys)
ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"
ADZUNA_APP_ID = "0c3b9bfa"
ADZUNA_APP_KEY = "87904b17c3da02bbd33d522cdd5e3596"

# Job Schema
class Job(BaseModel):
    title: str
    company: str
    location: str
    type: str  # Part-time, Consultant, etc.
    category: Optional[str]  # Women, Veterans, etc.
    skills_required: List[str]
    salary: Optional[str]
    apply_url: str

@app.get("/jobs", response_model=List[Job])
def get_jobs(
    skills: Optional[List[str]] = Query(None),
    work_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None
):
    return fetch_external_jobs(location, skills)

def fetch_external_jobs(location: Optional[str], skills: Optional[List[str]]):
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "where": location or "",
        "what": ",".join(skills) if skills else ""
    }
    
    response = requests.get(ADZUNA_API_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # Log API response for debugging
        logging.info(f"API Response: {data}")

        try:
            jobs = [
                Job(
                    title=job.get("title", "Unknown"),
                    company=job.get("company", {}).get("display_name", "Unknown"),
                    location=job.get("location", {}).get("display_name", "Remote"),
                    type="Part-time" if "part-time" in job.get("title", "").lower() else "Full-time",
                    category=None,  # No category data from Adzuna
                    skills_required=[],  # No skill data from Adzuna
                    salary=str(job.get("salary_min", "Unknown")),  # Ensure salary is a string
                    apply_url=job.get("redirect_url", "")
                ) for job in data.get("results", [])
            ]
            return jobs
        except Exception as e:
            logging.error(f"Error processing job data: {e}")
    
    logging.error(f"Failed to fetch jobs: {response.status_code} - {response.text}")
    return []
