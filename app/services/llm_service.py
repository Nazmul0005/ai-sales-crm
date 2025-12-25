"""
LLM service using Groq API for lead enrichment and email generation.
"""
import logging
import json
import re
from typing import Dict, Tuple, Optional
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_groq import ChatGroq
from langchain.messages import HumanMessage, SystemMessage

from app.models import Lead
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using Groq API."""
    
    def __init__(self):
        """Initialize LLM service with Groq client."""
        try:
            self.llm = ChatGroq(
                groq_api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens
            )
            logger.info(f"LLM Service initialized with model: {settings.llm_model}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}", exc_info=True)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def score_lead(self, lead: Lead) -> int:
        """
        Score a lead from 1-10 based on available information.
        
        Args:
            lead: Lead object to score
            
        Returns:
            Integer score between 1 and 10
        """
        try:
            logger.debug(f"Scoring lead: {lead.name}")
            
            system_prompt = """You are an expert B2B sales analyst. Score leads from 1-10 based on:
- Job seniority (C-level=10, VP=8, Director=7, Manager=5, IC=3)
- Company size indicators
- Industry relevance to B2B SaaS
- Data completeness

Return ONLY a single number from 1-10. No explanation."""
            
            user_prompt = f"""Score this lead:
Name: {lead.name}
Job Title: {lead.job_title or 'Unknown'}
Company: {lead.company or 'Unknown'}
Industry: {lead.industry or 'Unknown'}
Location: {lead.location or 'Unknown'}

Score (1-10):"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            score_text = response.content.strip()
            
            # Extract number from response
            score_match = re.search(r'\b(\d+)\b', score_text)
            if score_match:
                score = int(score_match.group(1))
                score = max(1, min(10, score))  # Clamp between 1-10
            else:
                logger.warning(f"Could not parse score from: {score_text}, defaulting to 5")
                score = 5
            
            logger.info(f"Lead {lead.name} scored: {score}")
            return score
            
        except Exception as e:
            logger.error(f"Error scoring lead {lead.name}: {e}", exc_info=True)
            return 5  # Default score on error
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def enrich_lead(self, lead: Lead) -> Dict[str, Optional[str]]:
        """
        Enrich missing lead information using LLM inference.
        
        Args:
            lead: Lead object with potentially missing fields
            
        Returns:
            Dictionary with enriched field values
        """
        try:
            logger.debug(f"Enriching lead: {lead.name}")
            
            # Check which fields are missing
            missing_fields = []
            if not lead.company:
                missing_fields.append("company")
            if not lead.industry:
                missing_fields.append("industry")
            if not lead.job_title:
                missing_fields.append("job_title")
            if not lead.location:
                missing_fields.append("location")
            
            if not missing_fields:
                logger.debug(f"No missing fields for {lead.name}, skipping enrichment")
                return {}
            
            system_prompt = """You are a data enrichment expert. Based on available information, 
infer likely values for missing fields using typical patterns and professional norms.
Return ONLY a JSON object with the missing fields. Be realistic and conservative."""
            
            user_prompt = f"""Enrich this lead profile:
Name: {lead.name}
Email: {lead.email}
Company: {lead.company or 'MISSING'}
Industry: {lead.industry or 'MISSING'}
Job Title: {lead.job_title or 'MISSING'}
Location: {lead.location or 'MISSING'}

Return JSON with ONLY the missing fields. Example:
{{"company": "TechCorp Inc.", "industry": "Technology", "job_title": "Marketing Manager", "location": "San Francisco, CA"}}

JSON:"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                enriched_data = json.loads(json_match.group())
                logger.info(f"Enriched {len(enriched_data)} fields for {lead.name}")
                return enriched_data
            else:
                logger.warning(f"Could not parse JSON from enrichment response for {lead.name}")
                return {}
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error during enrichment for {lead.name}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error enriching lead {lead.name}: {e}", exc_info=True)
            return {}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_persona(self, lead: Lead) -> str:
        """
        Generate a buyer persona description for the lead.
        
        Args:
            lead: Lead object
            
        Returns:
            Persona description string
        """
        try:
            logger.debug(f"Generating persona for: {lead.name}")
            
            system_prompt = """You are a buyer persona expert. Create a concise 2-sentence 
buyer persona based on the lead's profile. Focus on professional goals, challenges, and buying motivations."""
            
            user_prompt = f"""Create a buyer persona for:
Job Title: {lead.job_title or 'Professional'}
Company: {lead.company or 'Organization'}
Industry: {lead.industry or 'Business'}

Persona (2 sentences):"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            persona = response.content.strip()
            
            logger.info(f"Generated persona for {lead.name}: {persona[:50]}...")
            return persona
            
        except Exception as e:
            logger.error(f"Error generating persona for {lead.name}: {e}", exc_info=True)
            return f"Professional in {lead.industry or 'business'} sector seeking efficient solutions."
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def draft_email(self, lead: Lead, persona: str) -> Tuple[str, str]:
        """
        Draft a personalized outreach email.
        
        Args:
            lead: Lead object
            persona: Generated buyer persona
            
        Returns:
            Tuple of (subject_line, email_body)
        """
        try:
            logger.debug(f"Drafting email for: {lead.name}")
            
            system_prompt = """You are an expert sales copywriter. Write brief, personalized 
cold outreach emails. Keep it professional, value-focused, and under 100 words.

Format:
Subject: [compelling subject line under 50 chars]
Body: [3-4 sentence email with greeting, value prop, and CTA]"""
            
            user_prompt = f"""Write a personalized email for:
Name: {lead.name}
Title: {lead.job_title or 'Professional'}
Company: {lead.company or 'your organization'}
Persona: {persona}

Context: We offer an AI-powered CRM that helps sales teams automate lead scoring and outreach.

Email:"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            email_content = response.content.strip()
            
            # Parse subject and body
            subject_match = re.search(r'Subject:\s*(.+?)(?:\n|$)', email_content, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else f"Quick question for {lead.name}"
            
            # Extract body (everything after Subject line)
            body_match = re.search(r'Body:\s*(.+)', email_content, re.IGNORECASE | re.DOTALL)
            if body_match:
                body = body_match.group(1).strip()
            else:
                # If no "Body:" label, take everything after subject
                body = re.sub(r'Subject:.+?\n', '', email_content, flags=re.IGNORECASE).strip()
            
            # Ensure body starts with greeting if missing
            if not body.lower().startswith(('hi', 'hello', 'dear')):
                body = f"Hi {lead.name.split()[0]},\n\n{body}"
            
            logger.info(f"Drafted email for {lead.name} with subject: {subject}")
            return subject, body
            
        except Exception as e:
            logger.error(f"Error drafting email for {lead.name}: {e}", exc_info=True)
            default_subject = f"Streamline your sales process, {lead.name.split()[0]}"
            default_body = f"""Hi {lead.name.split()[0]},

I noticed you're in {lead.industry or 'the business'} sector and thought our AI-powered CRM might help streamline your sales operations.

Would you be open to a quick 15-minute conversation about automating lead scoring and outreach?

Best regards,
Sales Team"""
            return default_subject, default_body
    
    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_insights(self, stats: Dict) -> str:
        """
        Generate AI-powered insights from campaign statistics.
        
        Args:
            stats: Dictionary of campaign statistics
            
        Returns:
            Markdown-formatted insights
        """
        try:
            logger.debug("Generating campaign insights")
            
            system_prompt = """You are a sales analytics expert. Analyze campaign statistics 
and provide 3-4 actionable insights. Be specific, data-driven, and concise."""
            
            user_prompt = f"""Analyze this campaign:
Total Leads: {stats.get('total_leads', 0)}
Processed: {stats.get('processed_leads', 0)}
Average Score: {stats.get('avg_score', 0):.1f}
High Priority: {stats.get('high_priority', 0)}
Medium Priority: {stats.get('medium_priority', 0)}
Low Priority: {stats.get('low_priority', 0)}
Interested: {stats.get('interested_count', 0)}
Not Interested: {stats.get('not_interested_count', 0)}

Provide 3-4 key insights (use bullet points):"""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm.invoke(messages)
            insights = response.content.strip()
            
            logger.info("Generated campaign insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}", exc_info=True)
            return "- Campaign completed successfully\n- Review high-priority leads first\n- Consider follow-up strategy for interested leads"