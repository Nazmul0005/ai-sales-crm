"""
CSV handling service for reading and writing lead data.
"""
import pandas as pd
import logging
from typing import List, Optional
from pathlib import Path

from app.models import Lead, EnrichedLead
from app.config import settings

logger = logging.getLogger(__name__)

class CSVHandler:
    """Handles CSV operations for lead data."""
    
    def __init__(self, input_path: Optional[str] = None, output_path: Optional[str] = None):
        """
        Initialize CSV handler.
        
        Args:
            input_path: Path to input CSV file
            output_path: Path to output CSV file
        """
        self.input_path = input_path or settings.input_csv_path
        self.output_path = output_path or settings.output_csv_path
        logger.info(f"CSV Handler initialized with input: {self.input_path}, output: {self.output_path}")
    
    def read_leads(self) -> List[Lead]:
        """
        Read leads from CSV file.
        
        Returns:
            List of Lead objects
            
        Raises:
            FileNotFoundError: If input CSV doesn't exist
            ValueError: If CSV format is invalid
        """
        try:
            logger.info(f"Reading leads from {self.input_path}")
            
            # Check if file exists
            if not Path(self.input_path).exists():
                error_msg = f"Input CSV file not found: {self.input_path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # Read CSV with pandas
            df = pd.read_csv(self.input_path)
            logger.info(f"CSV loaded with {len(df)} rows")
            
            # Validate required columns
            required_columns = ['name', 'email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                error_msg = f"Missing required columns: {missing_columns}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # Convert to Lead objects
            leads = []
            for idx, row in df.iterrows():
                try:
                    lead = Lead(
                        name=row.get('name'),
                        email=row.get('email'),
                        company=row.get('company') if pd.notna(row.get('company')) else None,
                        industry=row.get('industry') if pd.notna(row.get('industry')) else None,
                        job_title=row.get('job_title') if pd.notna(row.get('job_title')) else None,
                        location=row.get('location') if pd.notna(row.get('location')) else None,
                        phone=row.get('phone') if pd.notna(row.get('phone')) else None
                    )
                    leads.append(lead)
                    logger.debug(f"Parsed lead {idx + 1}: {lead.name} ({lead.email})")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse row {idx + 1}: {e}")
                    continue
            
            logger.info(f"Successfully parsed {len(leads)} leads")
            return leads
            
        except FileNotFoundError:
            raise
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Error reading CSV: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)
    
    def write_leads(self, enriched_leads: List[EnrichedLead]) -> str:
        """
        Write enriched leads to CSV file.
        
        Args:
            enriched_leads: List of EnrichedLead objects
            
        Returns:
            Path to output CSV file
            
        Raises:
            ValueError: If writing fails
        """
        try:
            logger.info(f"Writing {len(enriched_leads)} enriched leads to {self.output_path}")
            
            # Ensure output directory exists
            output_dir = Path(self.output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionaries
            leads_data = [lead.dict() for lead in enriched_leads]
            
            # Create DataFrame
            df = pd.DataFrame(leads_data)
            
            # Reorder columns for better readability
            column_order = [
                'name', 'email', 'company', 'industry', 'job_title', 
                'location', 'phone', 'score', 'priority', 'persona',
                'email_subject', 'email_body', 'status', 'response_status',
                'processed_at', 'error_message'
            ]
            
            # Only include columns that exist
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Write to CSV
            df.to_csv(self.output_path, index=False)
            logger.info(f"Successfully wrote {len(df)} rows to {self.output_path}")
            
            return self.output_path
            
        except Exception as e:
            error_msg = f"Error writing CSV: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise ValueError(error_msg)
    
    def validate_csv_format(self) -> bool:
        """
        Validate input CSV format without reading all data.
        
        Returns:
            True if valid, False otherwise
        """
        try:
            df = pd.read_csv(self.input_path, nrows=1)
            required_columns = ['name', 'email']
            has_required = all(col in df.columns for col in required_columns)
            
            if has_required:
                logger.info("CSV format validation passed")
            else:
                logger.warning("CSV format validation failed: missing required columns")
                
            return has_required
            
        except Exception as e:
            logger.error(f"CSV validation error: {e}")
            return False