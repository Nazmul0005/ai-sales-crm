from datetime import datetime
from app.services.report_service import ReportService
from app.models import EnrichedLead, Lead

# Create dummy enriched leads for testing
leads = [
    EnrichedLead(
        name="John Doe",
        email="john@example.com",
        company="Tech Corp",
        industry="Software",
        job_title="CTO",
        score=9,
        priority="High",
        status="sent",
        response_status="interested",
        persona="Tech decision maker focused on innovation",
        processed_at=datetime.now()
    ),
    EnrichedLead(
        name="Jane Smith",
        email="jane@example.com",
        company="Business Inc",
        industry="Finance",
        job_title="Manager",
        score=5,
        priority="Medium",
        status="sent",
        response_status="no_response",
        persona="Operational manager seeking efficiency",
        processed_at=datetime.now()
    )
]

print(f"Testing report service with {len(leads)} dummy leads...")

try:
    service = ReportService()
    stats = service.calculate_stats(leads)
    report_path = service.generate_report(leads, stats, execution_time=5.5)
    print(f"✓ Report generated successfully: {report_path}")
    
    # Print stats summary
    print("\nCampaign Stats:")
    print(f"- Total: {stats.total_leads}")
    print(f"- Processed: {stats.processed_leads}")
    print(f"- Emails Sent: {stats.emails_sent}")
    print(f"- Interested: {stats.interested_count}")
    
except Exception as e:
    print(f"✗ Error: {e}")
