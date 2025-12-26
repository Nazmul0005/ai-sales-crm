"""
Configuration management for the AI Sales CRM application.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
import logging

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Groq API Configuration
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    llm_model: str = Field(default="mixtral-8x7b-32768", env="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=500, env="LLM_MAX_TOKENS")
    
    # SMTP Configuration
    smtp_host: str = Field(default="127.0.0.1", env="SMTP_HOST")
    smtp_port: int = Field(default=1025, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Application Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_concurrent_leads: int = Field(default=5, env="MAX_CONCURRENT_LEADS")
    
    # File Paths
    input_csv_path: str = Field(default="data/test.csv")
    output_csv_path: str = Field(default="data/leads_output.csv")
    reports_dir: str = Field(default="reports")
    logs_dir: str = Field(default="logs")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

# Initialize settings
try:
    settings = Settings()
    logger = setup_logging(settings.log_level)
    logger.info("Configuration loaded successfully")
except Exception as e:
    print(f"Error loading configuration: {e}")
    raise