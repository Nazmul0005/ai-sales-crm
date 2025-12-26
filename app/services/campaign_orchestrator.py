"""
Campaign orchestration service - main pipeline coordinator.
"""
import logging
import asyncio
import random
from datetime import datetime
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor

from app.models import Lead, EnrichedLead, CampaignStats, CampaignResponse
from app.services.csv_handler import CSVHandler
from app.services.llm_service import LLMService
from app.services.email_service import EmailService
from app.services.report_service import ReportService
from app.config import settings

logger = logging.getLogger(__name__)

class CampaignOrchestrator:
    """Orchestrates the complete campaign pipeline."""
    
    def __init__(self):
        """Initialize campaign orchestrator with all services."""
        try:
            self.csv_handler = CSVHandler()
            self.llm_service = LLMService()
            self.email_service = EmailService()
            self.report_service = ReportService()
            logger.info("Campaign Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Campaign Orchestrator: {e}", exc_info=True)
            raise
    
    async def run_campaign(self) -> CampaignResponse:
        """
        Execute the complete campaign pipeline.
        
        Returns:
            CampaignResponse with results and statistics
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("STARTING CAMPAIGN EXECUTION")
        logger.info("=" * 80)
        
        try:
            # Step 1: Read leads from CSV
            logger.info("Step 1/6: Reading leads from CSV...")
            leads = self.csv_handler.read_leads()
            logger.info(f"✓ Loaded {len(leads)} leads")
            
            # Step 2: Process leads (enrich, score, generate emails)
            logger.info(f"Step 2/6: Processing {len(leads)} leads...")
            enriched_leads = await self._process_leads_batch(leads)
            logger.info(f"✓ Processed {len(enriched_leads)} leads")
            
            # Step 3: Send emails
            logger.info("Step 3/6: Sending outreach emails...")
            await self._send_campaign_emails(enriched_leads)
            logger.info("✓ Emails sent")
            
            # Step 4: Simulate responses (for demo)
            logger.info("Step 4/6: Simulating lead responses...")
            self._simulate_responses(enriched_leads)
            logger.info("✓ Responses simulated")
            
            # Step 5: Write results to CSV
            logger.info("Step 5/6: Writing results to CSV...")
            output_path = self.csv_handler.write_leads(enriched_leads)
            logger.info(f"✓ Results written to {output_path}")
            
            # Step 6: Generate report
            logger.info("Step 6/6: Generating campaign report...")
            stats = self.report_service.calculate_stats(enriched_leads)
            execution_time = (datetime.now() - start_time).total_seconds()
            report_path = self.report_service.generate_report(
                enriched_leads,
                stats,
                execution_time
            )
            logger.info(f"✓ Report generated: {report_path}")
            
            # Final summary
            logger.info("=" * 80)
            logger.info("CAMPAIGN COMPLETED SUCCESSFULLY")
            logger.info(f"Total Time: {execution_time:.2f} seconds")
            logger.info(f"Leads Processed: {stats.processed_leads}/{stats.total_leads}")
            logger.info(f"Emails Sent: {stats.emails_sent}")
            logger.info(f"Average Score: {stats.avg_score:.1f}/10")
            logger.info("=" * 80)
            
            return CampaignResponse(
                success=True,
                message="Campaign completed successfully",
                stats=stats,
                report_path=report_path,
                output_csv_path=output_path,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Campaign execution failed: {e}", exc_info=True)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CampaignResponse(
                success=False,
                message=f"Campaign failed: {str(e)}",
                stats=None,
                report_path=None,
                output_csv_path=None,
                execution_time=execution_time
            )
    
    async def _process_leads_batch(self, leads: List[Lead]) -> List[EnrichedLead]:
        """
        Process leads in batches with concurrency control.
        
        Args:
            leads: List of raw leads
            
        Returns:
            List of enriched leads
        """
        logger.info(f"Processing leads with max concurrency: {settings.max_concurrent_leads}")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(settings.max_concurrent_leads)
        
        # Process all leads concurrently
        tasks = [self._process_single_lead(lead, semaphore) for lead in leads]
        enriched_leads = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log them
        valid_leads = []
        for idx, result in enumerate(enriched_leads):
            if isinstance(result, Exception):
                logger.error(f"Lead {idx+1} processing failed: {result}")
            else:
                valid_leads.append(result)
        
        logger.info(f"Successfully processed {len(valid_leads)}/{len(leads)} leads")
        return valid_leads
    
    async def _process_single_lead(
        self,
        lead: Lead,
        semaphore: asyncio.Semaphore
    ) -> EnrichedLead:
        """
        Process a single lead through the enrichment pipeline.
        
        Args:
            lead: Lead object to process
            semaphore: Semaphore for concurrency control
            
        Returns:
            Enriched lead object
        """
        async with semaphore:
            try:
                logger.debug(f"Processing lead: {lead.name}")
                
                # Run LLM operations in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                
                with ThreadPoolExecutor() as executor:
                    # Score lead
                    score = await loop.run_in_executor(
                        executor,
                        self.llm_service.score_lead,
                        lead
                    )
                    
                    # Enrich missing fields
                    enrichment_data = await loop.run_in_executor(
                        executor,
                        self.llm_service.enrich_lead,
                        lead
                    )
                    
                    # Apply enrichment
                    enriched_lead_data = lead.dict()
                    enriched_lead_data.update(enrichment_data)
                    temp_lead = Lead(**enriched_lead_data)
                    
                    # Generate persona
                    persona = await loop.run_in_executor(
                        executor,
                        self.llm_service.generate_persona,
                        temp_lead
                    )
                    
                    # Draft email
                    email_subject, email_body = await loop.run_in_executor(
                        executor,
                        self.llm_service.draft_email,
                        temp_lead,
                        persona
                    )
                
                # Determine priority based on score
                if score >= 8:
                    priority = "High"
                elif score >= 5:
                    priority = "Medium"
                else:
                    priority = "Low"
                
                # Create enriched lead
                enriched_lead = EnrichedLead(
                    **enriched_lead_data,
                    score=score,
                    priority=priority,
                    persona=persona,
                    email_subject=email_subject,
                    email_body=email_body,
                    status="pending",
                    processed_at=datetime.now()
                )
                
                logger.info(f"✓ Processed: {lead.name} | Score: {score} | Priority: {priority}")
                return enriched_lead
                
            except Exception as e:
                logger.error(f"Error processing lead {lead.name}: {e}", exc_info=True)
                
                # Return a lead with error status
                return EnrichedLead(
                    **lead.dict(),
                    status="failed",
                    error_message=str(e),
                    processed_at=datetime.now()
                )
    
    async def _send_campaign_emails(self, enriched_leads: List[EnrichedLead]) -> None:
        """
        Send emails to all processed leads.
        
        Args:
            enriched_leads: List of enriched leads with drafted emails
        """
        logger.info("Sending emails to leads...")
        
        # Prepare email data
        email_tasks = []
        for lead in enriched_leads:
            if lead.status == "pending" and lead.email_body:
                email_tasks.append((
                    lead.email,
                    lead.email_subject or f"Quick question for {lead.name}",
                    lead.email_body,
                    lead.name
                ))
        
        logger.info(f"Sending {len(email_tasks)} emails...")
        
        # Send emails one by one (to avoid overwhelming MailHog)
        sent_count = 0
        failed_count = 0
        
        for to_email, subject, body, name in email_tasks:
            try:
                success = await self.email_service.send_email(
                    to_email,
                    subject,
                    body,
                    name
                )
                
                if success:
                    # Update lead status
                    for lead in enriched_leads:
                        if lead.email == to_email:
                            lead.status = "sent"
                            break
                    sent_count += 1
                else:
                    failed_count += 1
                    # Update lead status
                    for lead in enriched_leads:
                        if lead.email == to_email:
                            lead.status = "failed"
                            lead.error_message = "Email sending failed"
                            break
                
                # Small delay to avoid overwhelming SMTP
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error sending email to {to_email}: {e}")
                failed_count += 1
        
        logger.info(f"Email sending complete: {sent_count} sent, {failed_count} failed")
    
    def _simulate_responses(self, enriched_leads: List[EnrichedLead]) -> None:
        """
        Simulate lead responses for demo purposes.
        
        Args:
            enriched_leads: List of enriched leads
        """
        logger.info("Simulating lead responses...")
        
        for lead in enriched_leads:
            if lead.status == "sent":
                # Simulate responses based on lead score
                # Higher score = higher chance of interest
                if lead.score >= 8:
                    # High score: 50% interested, 20% not interested, 30% no response
                    response = random.choices(
                        ["interested", "not_interested", "no_response"],
                        weights=[0.5, 0.2, 0.3]
                    )[0]
                elif lead.score >= 5:
                    # Medium score: 30% interested, 20% not interested, 50% no response
                    response = random.choices(
                        ["interested", "not_interested", "no_response"],
                        weights=[0.3, 0.2, 0.5]
                    )[0]
                else:
                    # Low score: 10% interested, 30% not interested, 60% no response
                    response = random.choices(
                        ["interested", "not_interested", "no_response"],
                        weights=[0.1, 0.3, 0.6]
                    )[0]
                
                lead.response_status = response
                logger.debug(f"Lead {lead.name}: {response}")
        
        logger.info("Response simulation complete")
