"""
Pydantic models for lead data structures.
"""
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class Lead(BaseModel):
    """Base lead model from input CSV."""
    
    name: str = Field(..., description="Lead's full name")
    email: EmailStr = Field(..., description="Lead's email address")
    company: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry sector")
    job_title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Geographic location")
    phone: Optional[str] = Field(None, description="Phone number")
    
    class Config:
        str_strip_whitespace = True

class EnrichedLead(Lead):
    """Enriched lead model with AI-generated fields."""
    
    score: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Lead quality score (1-10)"
    )
    priority: Literal["High", "Medium", "Low"] = Field(
        default="Medium",
        description="Lead priority level"
    )
    persona: Optional[str] = Field(
        None,
        description="AI-generated buyer persona"
    )
    email_subject: Optional[str] = Field(
        None,
        description="Personalized email subject line"
    )
    email_body: Optional[str] = Field(
        None,
        description="Personalized email body"
    )
    status: Literal["pending", "sent", "failed", "interested", "not_interested", "no_response"] = Field(
        default="pending",
        description="Current lead status"
    )
    response_status: Optional[Literal["interested", "not_interested", "no_response"]] = Field(
        None,
        description="Simulated response status"
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when lead was processed"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )
    
    @validator('priority', always=True)
    def set_priority_from_score(cls, v, values):
        """Automatically set priority based on score."""
        score = values.get('score', 5)
        if score >= 8:
            return "High"
        elif score >= 5:
            return "Medium"
        else:
            return "Low"
    
    class Config:
        str_strip_whitespace = True

class CampaignStats(BaseModel):
    """Statistics for campaign reporting."""
    
    total_leads: int = Field(..., description="Total number of leads")
    processed_leads: int = Field(..., description="Successfully processed leads")
    failed_leads: int = Field(..., description="Failed processing leads")
    emails_sent: int = Field(..., description="Emails successfully sent")
    high_priority: int = Field(..., description="High priority leads count")
    medium_priority: int = Field(..., description="Medium priority leads count")
    low_priority: int = Field(..., description="Low priority leads count")
    avg_score: float = Field(..., description="Average lead score")
    interested_count: int = Field(default=0, description="Interested responses")
    not_interested_count: int = Field(default=0, description="Not interested responses")
    no_response_count: int = Field(default=0, description="No response count")
    top_personas: list[tuple[str, int]] = Field(
        default=[],
        description="Top 5 personas and their counts"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "total_leads": 20,
                "processed_leads": 18,
                "failed_leads": 2,
                "emails_sent": 18,
                "high_priority": 5,
                "medium_priority": 10,
                "low_priority": 3,
                "avg_score": 6.5,
                "interested_count": 6,
                "not_interested_count": 4,
                "no_response_count": 8
            }
        }

class CampaignResponse(BaseModel):
    """API response for campaign execution."""
    
    success: bool = Field(..., description="Whether campaign completed successfully")
    message: str = Field(..., description="Status message")
    stats: Optional[CampaignStats] = Field(None, description="Campaign statistics")
    report_path: Optional[str] = Field(None, description="Path to generated report")
    output_csv_path: Optional[str] = Field(None, description="Path to output CSV")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")