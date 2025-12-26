# 🚀 AI-Powered Sales Campaign CRM
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-teal?logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)
![Groq](https://img.shields.io/badge/Groq-LLM-black?logo=groq)
![LLM](https://img.shields.io/badge/LLM-Llama--3.3--70B-purple)
![AI Powered](https://img.shields.io/badge/AI-Powered-orange)
![SMTP](https://img.shields.io/badge/SMTP-MailHog-yellow)
![Email Automation](https://img.shields.io/badge/Email-Automation-red)
![CSV](https://img.shields.io/badge/Data-CSV-lightgrey)
![Analytics](https://img.shields.io/badge/Campaign-Analytics-brightgreen)
![Reports](https://img.shields.io/badge/Reports-Markdown-blueviolet)
![Dockerized](https://img.shields.io/badge/Fully-Dockerized-2496ED?logo=docker)
![API](https://img.shields.io/badge/API-REST-success)
![Built By](https://img.shields.io/badge/Built%20By-Nazmul%20Islam-black)

A lightweight, AI-powered CRM system that automates lead scoring, enrichment, and personalized outreach campaigns using Groq LLM and MailHog.

<p align="center">
  <img src="assets/ai-sales-crm.png" alt="Project Screenshot" width="800"/>
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1QjA6Yd3DfF6Q5blO_6W7-jFjBcu3r4dK/view?usp=sharing">
    <img src="/video-thumbnail.png" alt="Watch Video" width="700"/>
  </a>
</p>

## ✨ Features

- **🎯 AI Lead Scoring**: Automatically score leads 1-10 based on job title, industry, and company
- **📊 Lead Enrichment**: Fill missing lead data using AI inference
- **👤 Persona Generation**: Create buyer personas for targeted outreach
- **✉️ Personalized Emails**: Generate customized cold emails for each lead
- **📧 Email Automation**: Send emails via SMTP with MailHog for testing
- **📈 Campaign Analytics**: Comprehensive reports with AI-generated insights
- **🔄 Response Simulation**: Demo-ready with simulated lead responses

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐     ┌──────────────┐  │
│  │ CSV Handler  │──▶ │ LLM Service │───▶ │Email Service │  │
│  │              │    │   (Groq)     │     │  (MailHog)   │  │
│  └──────────────┘    └──────────────┘     └──────────────┘  │
│         │                    │                    │         │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │               Campaign Orchestrator                  │   │
│  │      (Coordinates entire pipeline with logging)      │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                              │
│                              ▼                              │
│                    ┌──────────────────┐                     │
│                    │  Report Service  │                     │
│                    │  (Markdown + AI) │                     │
│                    └──────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- Docker & Docker Compose
- Groq API Key (free from [console.groq.com](https://console.groq.com))
- 4GB RAM minimum
- 2GB disk space

## 🚀 Quick Start

### 1️⃣ Clone and Setup

```bash
# Clone the repository
git clone https://github.com/Nazmul0005/ai-sales-crm.git
cd ai-sales-crm

# Copy environment template
cp .env.example .env

# Edit .env and add your Groq API key
nano .env  # or use your preferred editor
```

### 2️⃣ Configure Environment

Edit `.env` file:

```bash
GROQ_API_KEY=your_actual_groq_api_key_here
SMTP_HOST=mailhog
SMTP_PORT=1025
LOG_LEVEL=INFO
```

### 3️⃣ Run the Application

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up -d
```

### 4️⃣ Execute Campaign

**Option A: Via API (Recommended)**

```bash
# Trigger campaign via API
curl -X POST http://localhost:8000/campaign/run

# Check status
curl http://localhost:8000/campaign/status
```

**Option B: Via Web Interface**

1. Open http://localhost:8000/docs
2. Find `/campaign/run` endpoint
3. Click "Try it out" → "Execute"

### 5️⃣ View Results

- **MailHog UI**: http://localhost:8025 (see all sent emails)
- **FastAPI Docs**: http://localhost:8000/docs
- **Output CSV**: `data/leads_output.csv`
- **Campaign Report**: `reports/campaign_summary_TIMESTAMP.md`
- **Logs**: `logs/app.log`

## 📁 Project Structure

```
ai-sales-crm/
├── app/
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration & logging
│   ├── models.py                    # Pydantic models
│   └── services/
│       ├── csv_handler.py           # CSV operations
│       ├── llm_service.py           # Groq LLM integration
│       ├── email_service.py         # SMTP email sending
│       ├── report_service.py        # Report generation
│       └── campaign_orchestrator.py # Main pipeline
├── data/ 
│   ├── leads_input.csv              # Sample input leads
│   └── leads_output.csv             # Enriched results (generated)
├── reports/
│   └── campaign_summary_*.md        # Generated reports
├── logs/
│   └── app.log                      # Application logs
├── docker-compose.yml               # Docker services
├── Dockerfile                       # App container
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables
└── README.md                        # This file
```

## 🔧 Configuration

### LLM Settings

Modify in `.env`:

```bash
LLM_MODEL=llama-3.3-70b-versatile     # Groq model (fast & accurate)
LLM_TEMPERATURE=0.7                   # Creativity level (0-1)
LLM_MAX_TOKENS=500                    # Max response length
MAX_CONCURRENT_LEADS=5                # Parallel processing limit
```

### Input CSV Format

Required columns:

- `name` (required)
- `email` (required)
- `company` (optional)
- `industry` (optional)
- `job_title` (optional)
- `location` (optional)
- `phone` (optional)

See `data/leads_input.csv` for examples.

## 📊 Output Files

### Enriched CSV (`data/leads_output.csv`)

Contains all original fields plus:

- `score` - Lead quality score (1-10)
- `priority` - High/Medium/Low
- `persona` - AI-generated buyer persona
- `email_subject` - Personalized subject line
- `email_body` - Personalized email content
- `status` - sent/failed/pending
- `response_status` - interested/not_interested/no_response
- `processed_at` - Timestamp
- `error_message` - If processing failed

### Campaign Report (`reports/campaign_summary_*.md`)

Includes:

- Campaign overview & stats
- Priority distribution
- Score distribution chart
- Response analysis
- Top buyer personas
- Top 5 high-priority leads
- AI-generated insights
- Next steps recommendations

## 🛠️ Development

### Run Without Docker

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run MailHog separately
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# Set environment variables
export GROQ_API_KEY=your_key_here
export SMTP_HOST=localhost

# Run application
uvicorn app.main:app --reload --port 8000
```

### Run Tests

```bash
# Test SMTP connection
curl http://localhost:8000/test/smtp

# Health check
curl http://localhost:8000/health

# Check campaign status
curl http://localhost:8000/campaign/status
```

### View Logs

```bash
# Follow logs in real-time
docker compose logs -f crm-api

# Or check log file
tail -f logs/app.log
```

## 🎯 API Endpoints

| Endpoint             | Method | Description           |
| -------------------- | ------ | --------------------- |
| `/`                | GET    | API information       |
| `/health`          | GET    | Health check          |
| `/campaign/run`    | POST   | Execute campaign      |
| `/campaign/status` | GET    | Check campaign status |
| `/test/smtp`       | GET    | Test email connection |
| `/docs`            | GET    | Interactive API docs  |

## 🔒 Error Handling

The system includes comprehensive error handling:

- **Retry logic** for LLM API calls (3 attempts with exponential backoff)
- **Graceful degradation** (default values if AI fails)
- **Detailed logging** at every step
- **Failed lead tracking** with error messages
- **SMTP connection testing** on startup

## 📈 Performance

- Processes 20 leads in ~60-90 seconds
- Concurrent processing (5 leads at a time by default)
- Average 3-4 seconds per lead
- Optimized for demo readiness

## 🐛 Troubleshooting

### Issue: "Groq API key not found"

```bash
# Check your .env file has the key
cat .env | grep GROQ_API_KEY

# Restart containers after editing .env
docker compose down && docker compose up --build
```

### Issue: "SMTP connection failed"

```bash
# Check MailHog is running
docker compose ps

# Test SMTP connection
curl http://localhost:8000/test/smtp

# Check MailHog UI is accessible
open http://localhost:8025
```

### Issue: "CSV file not found"

```bash
# Ensure data directory exists
mkdir -p data

# Check sample CSV exists
ls -la data/leads_input.csv
```

### Issue: "Out of memory"

```bash
# Reduce concurrent processing in .env
MAX_CONCURRENT_LEADS=3

# Or increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory
```

## 🎨 Customization

### Modify Email Templates

Edit `app/services/email_service.py` → `_create_html_email()`

### Change LLM Prompts

Edit `app/services/llm_service.py` → system prompts in each function

### Add Custom Fields

1. Update `app/models.py` → EnrichedLead model
2. Update CSV processing logic
3. Update report generation

### Switch LLM Provider

Replace LangChain's `ChatGroq` with any other provider:

- `ChatOpenAI` for OpenAI
- `ChatAnthropic` for Claude
- `ChatOllama` for local models

## 📝 Sample Output

### Console Output

```
================================================================================
STARTING CAMPAIGN EXECUTION
================================================================================
Step 1/6: Reading leads from CSV...
✓ Loaded 23 leads
Step 2/6: Processing 23 leads...
✓ Processed: Sarah Johnson | Score: 9 | Priority: High
✓ Processed: Michael Chen | Score: 8 | Priority: High
...
✓ Processed 23 leads
Step 3/6: Sending outreach emails...
✓ Emails sent
Step 4/6: Simulating lead responses...
✓ Responses simulated
Step 5/6: Writing results to CSV...
✓ Results written to data/leads_output.csv
Step 6/6: Generating campaign report...
✓ Report generated: reports/campaign_summary_20241225_143022.md
================================================================================
CAMPAIGN COMPLETED SUCCESSFULLY
Total Time: 78.45 seconds
Leads Processed: 23/23
Emails Sent: 23
Average Score: 6.8/10
================================================================================
```

## 🤝 Contributing

This is a demo project for interview purposes. Feel free to fork and customize!

## 📄 License

MIT License - feel free to use this code for learning and development.

## 🙋 Support

For questions or issues:

1. Check the logs: `logs/app.log`
2. Review troubleshooting section above
3. Test individual components using API endpoints

## 🎉 Demo Checklist For Execution

- [ ] `.env` file configured with valid Groq API key
- [ ] `docker compose up` runs successfully
- [ ] MailHog UI accessible at http://localhost:8025
- [ ] Campaign executes via `/campaign/run`
- [ ] Emails visible in MailHog
- [ ] Output CSV generated with enriched data
- [ ] Campaign report generated with insights
- [ ] Logs show successful processing

---

**Built By Nazmul Islam**
