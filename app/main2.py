from app.services.report_service import ReportService
from app.services.csv_handler import CSVHandler

# Load enriched leads
handler = CSVHandler()
leads = handler.read_leads()  # Assuming processed

service = ReportService()
stats = service.calculate_stats(leads)
report_path = service.generate_report(leads, stats, 60.0)

print(f"Report: {report_path}")