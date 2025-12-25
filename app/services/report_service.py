"""
Report generation service for campaign summaries.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import List
from collections import Counter

from app.models import EnrichedLead, CampaignStats
from app.config import settings
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class ReportService:
    """Service for generating campaign reports."""
    
    def __init__(self):
        """Initialize report service."""
        self.reports_dir = Path(settings.reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.llm_service = LLMService()
        logger.info(f"Report Service initialized, reports directory: {self.reports_dir}")
    
    def calculate_stats(self, leads: List[EnrichedLead]) -> CampaignStats:
        """
        Calculate campaign statistics from enriched leads.
        
        Args:
            leads: List of enriched lead objects
            
        Returns:
            CampaignStats object
        """
        try:
            logger.debug("Calculating campaign statistics")
            
            total_leads = len(leads)
            processed_leads = sum(1 for lead in leads if lead.status in ["sent", "interested", "not_interested", "no_response"])
            failed_leads = sum(1 for lead in leads if lead.status == "failed")
            emails_sent = sum(1 for lead in leads if lead.status == "sent" or lead.response_status)
            
            # Priority counts
            high_priority = sum(1 for lead in leads if lead.priority == "High")
            medium_priority = sum(1 for lead in leads if lead.priority == "Medium")
            low_priority = sum(1 for lead in leads if lead.priority == "Low")
            
            # Average score
            scores = [lead.score for lead in leads if lead.score]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Response counts
            interested_count = sum(1 for lead in leads if lead.response_status == "interested")
            not_interested_count = sum(1 for lead in leads if lead.response_status == "not_interested")
            no_response_count = sum(1 for lead in leads if lead.response_status == "no_response")
            
            # Top personas
            personas = [lead.persona for lead in leads if lead.persona]
            persona_counter = Counter(personas)
            top_personas = persona_counter.most_common(5)
            
            stats = CampaignStats(
                total_leads=total_leads,
                processed_leads=processed_leads,
                failed_leads=failed_leads,
                emails_sent=emails_sent,
                high_priority=high_priority,
                medium_priority=medium_priority,
                low_priority=low_priority,
                avg_score=round(avg_score, 2),
                interested_count=interested_count,
                not_interested_count=not_interested_count,
                no_response_count=no_response_count,
                top_personas=top_personas
            )
            
            logger.info(f"Statistics calculated: {processed_leads}/{total_leads} leads processed")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}", exc_info=True)
            raise
    
    def generate_report(
        self,
        leads: List[EnrichedLead],
        stats: CampaignStats,
        execution_time: float
    ) -> str:
        """
        Generate a comprehensive campaign report in Markdown format.
        
        Args:
            leads: List of enriched leads
            stats: Campaign statistics
            execution_time: Total execution time in seconds
            
        Returns:
            Path to generated report file
        """
        try:
            logger.info("Generating campaign report")
            
            # Generate AI insights
            try:
                insights = self.llm_service.generate_insights(stats.dict())
            except Exception as e:
                logger.warning(f"Could not generate AI insights: {e}")
                insights = "- Campaign completed successfully\n- Review results for follow-up actions"
            
            # Create report filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"campaign_summary_{timestamp}.md"
            report_path = self.reports_dir / report_filename
            
            # Build report content
            report_content = self._build_report_content(leads, stats, insights, execution_time)
            
            # Write report to file
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Report generated successfully: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            raise
    
    def _build_report_content(
        self,
        leads: List[EnrichedLead],
        stats: CampaignStats,
        insights: str,
        execution_time: float
    ) -> str:
        """
        Build the markdown content for the report.
        
        Args:
            leads: List of enriched leads
            stats: Campaign statistics
            insights: AI-generated insights
            execution_time: Execution time in seconds
            
        Returns:
            Markdown formatted report
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Score distribution
        score_distribution = self._get_score_distribution(leads)
        
        # Top leads
        top_leads = sorted(
            [lead for lead in leads if lead.status != "failed"],
            key=lambda x: x.score,
            reverse=True
        )[:5]
        
        report = f"""# 📊 AI Sales Campaign Report

**Generated:** {timestamp}  
**Execution Time:** {execution_time:.2f} seconds

---

## 📈 Campaign Overview

| Metric | Value |
|--------|-------|
| **Total Leads** | {stats.total_leads} |
| **Successfully Processed** | {stats.processed_leads} |
| **Failed** | {stats.failed_leads} |
| **Emails Sent** | {stats.emails_sent} |
| **Average Lead Score** | {stats.avg_score:.1f}/10 |

---

## 🎯 Priority Distribution

```
High Priority:   {stats.high_priority} leads ({stats.high_priority/stats.total_leads*100:.1f}%)
Medium Priority: {stats.medium_priority} leads ({stats.medium_priority/stats.total_leads*100:.1f}%)
Low Priority:    {stats.low_priority} leads ({stats.low_priority/stats.total_leads*100:.1f}%)
```

### Priority Breakdown Chart
```
High   : {'█' * (stats.high_priority * 2)}  ({stats.high_priority})
Medium : {'█' * (stats.medium_priority * 2)} ({stats.medium_priority})
Low    : {'█' * (stats.low_priority * 2)}    ({stats.low_priority})
```

---

## 📊 Lead Score Distribution

{score_distribution}

---

## 📧 Response Analysis

| Status | Count | Percentage |
|--------|-------|------------|
| **Interested** | {stats.interested_count} | {stats.interested_count/stats.emails_sent*100:.1f}% |
| **Not Interested** | {stats.not_interested_count} | {stats.not_interested_count/stats.emails_sent*100:.1f}% |
| **No Response** | {stats.no_response_count} | {stats.no_response_count/stats.emails_sent*100:.1f}% |

---

## 👥 Top Buyer Personas

"""
        # Add top personas
        for idx, (persona, count) in enumerate(stats.top_personas, 1):
            report += f"{idx}. **{persona[:80]}{'...' if len(persona) > 80 else ''}** ({count} leads)\n"
        
        report += f"""

---

## 🏆 Top 5 High-Priority Leads

"""
        # Add top leads table
        for idx, lead in enumerate(top_leads, 1):
            report += f"""
### {idx}. {lead.name} - Score: {lead.score}/10

- **Company:** {lead.company or 'N/A'}
- **Title:** {lead.job_title or 'N/A'}
- **Industry:** {lead.industry or 'N/A'}
- **Email:** {lead.email}
- **Status:** {lead.status}
- **Persona:** {lead.persona[:100] if lead.persona else 'N/A'}

"""

        report += f"""---

## 🤖 AI-Generated Insights

{insights}

---

## 📋 Next Steps

1. **Immediate Follow-up:** Contact the {stats.high_priority} high-priority leads within 24 hours
2. **Nurture Campaign:** Set up automated follow-ups for medium-priority leads
3. **Re-engagement:** Plan a secondary campaign for no-response leads after 1 week
4. **Analysis:** Review interested leads for common patterns and adjust targeting

---

## 🔍 Campaign Details

- **Total Processing Time:** {execution_time:.2f} seconds
- **Average Time per Lead:** {execution_time/stats.total_leads:.2f} seconds
- **Success Rate:** {stats.processed_leads/stats.total_leads*100:.1f}%
- **Email Delivery Rate:** {stats.emails_sent/stats.processed_leads*100:.1f}%

---

*Report generated by AI Sales CRM v1.0*
"""
        
        return report
    
    def _get_score_distribution(self, leads: List[EnrichedLead]) -> str:
        """
        Generate score distribution visualization.
        
        Args:
            leads: List of enriched leads
            
        Returns:
            Markdown formatted distribution chart
        """
        score_ranges = {
            "9-10 (Excellent)": 0,
            "7-8 (Good)": 0,
            "5-6 (Average)": 0,
            "3-4 (Below Average)": 0,
            "1-2 (Poor)": 0
        }
        
        for lead in leads:
            if lead.score >= 9:
                score_ranges["9-10 (Excellent)"] += 1
            elif lead.score >= 7:
                score_ranges["7-8 (Good)"] += 1
            elif lead.score >= 5:
                score_ranges["5-6 (Average)"] += 1
            elif lead.score >= 3:
                score_ranges["3-4 (Below Average)"] += 1
            else:
                score_ranges["1-2 (Poor)"] += 1
        
        distribution = "```\n"
        for range_name, count in score_ranges.items():
            bar = "█" * count
            distribution += f"{range_name:20} {bar} ({count})\n"
        distribution += "```"
        
        return distribution