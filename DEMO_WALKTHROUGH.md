## 🎬 Part 1: Introduction (0:00 - 0:45)

> "Hello! Today I'm going to demonstrate an **AI-Powered Sales Campaign CRM**.
>
> This project solves that by automating the entire pipeline using **Generative AI**. It takes a raw list of leads, uses a **Groq LLM** to research and score them, generates highly personalized 'buyer personas', and drafts custom outreach emails for each one.
>
> Let me show you how it works under the hood and then run a live campaign."

---

## 🏗️ Part 2: Architecture & Setup (0:45 - 1:30)

**Action:**

- Switch screen share to VS Code.
- Open `docker-compose.yml`.

**Script:**

> "First, a quick look at the tech stack. The entire system is containerized using **Docker**.
>
> We have three main services running here:
>
> 1. **The Core App**: Built with **FastAPI**, which handles the logic.
> 2. **Email Service**: I use **MailHog** to intercept and display emails locally, so I don't spam real people during testing.
> 3. **LLM Integration**: I am using **Groq**, which gives me incredibly fast inference speeds for real-time processing."

**Action:**

- Open `.env`.

**Script:**

> "Configuration is simple. I just set my `GROQ_API_KEY` here in the environment file, and I can tweak settings like the 'creativity' (temperature) of the AI or the maximum concurrent leads to process."

---

## 🚀 Part 3: Live Demo Execution (1:30 - 3:00)

**Action:**

- Open the integrated terminal in VS Code.
- Run: `docker compose up --build`
- *Wait a moment for logs to show "Application ready to accept requests"*

**Script:**

> "Let's spin it up. I'm running `docker compose up`. You can see the services starting... verifying the SMTP connection... and we are live!"

**Action:**

- Open your browser to `http://localhost:8000/docs`.

**Script:**

> "Now I'm at the Swagger UI. This is where we can interact with our API.
>
> I'm going to trigger the `/campaign/run` endpoint. This simulates a user starting a new outreach campaign."

**Action:**

- Click "Try it out" -> "Execute" on the `/campaign/run` endpoint.
- **IMMEDIATELY** switch back to the VS Code Terminal to show the logs scrolling.

**Script:**

> "I've hit execute. Watch the logs here.
>
> You can see the **Campaign Orchestrator** picking up the leads from our CSV file.
>
> Right now:
>
> 1. It's reading the leads.
> 2. It's sending them to Groq to analyze their job titles and companies.
> 3. It's generating a 'match score' from 1 to 10.
> 4. And finally, it's writing a unique email for each person based on their specific persona."

---

## 📧 Part 4: Viewing Results (3:00 - 4:00)

**Action:**

- Switch browser tab to MailHog: `http://localhost:8025`.

**Script:**

> "The campaign is finished. Let's see the results. I'm heading over to MailHog.
>
> Look at this! We have emails generated for our leads.
> Let's open one...
>
> *[Click on an email]*
>
> Notice the subject line isn't generic. And the body text references their specific industry and role. The AI realized this lead was a 'Tech Decision Maker' and adjusted the tone to be more technical. That's the power of persona-based generation."

**Action:**

- Switch back to VS Code.
- Open the newly generated report in `reports/` folder (e.g., `reports/campaign_summary_....md`).
- Open preview (Ctrl+Shift+V or Command+Shift+V).

**Script:**

> "Finally, the system generates a comprehensive report.
>
> It summarizes the campaign performance, shows the distribution of lead scores, and even gives us AI-generated insights on how to improve our next campaign."

---

## 💻 Part 5: Code Walkthrough (Optional) (4:00 - 4:45)

**Action:**

- Open `app/services/campaign_orchestrator.py`.

**Script:**

> "Briefly, let me show you the brain of the operation: the `CampaignOrchestrator`.
>
> Here in the `run_campaign` method, we handle the entire pipeline asynchronously. We use a semaphore to limit concurrent LLM requests to ensure we don't hit rate limits, while still processing multiple leads in parallel for speed."

---

## 🏁 Part 6: Conclusion (4:45 - 5:00)

**Action:**

- Switch camera back to yourself.

**Script:**

> "So that is the AI Sales CRM. It demonstrates how modern AI can transform manual workflows into intelligent, automated pipelines.
>
> Thanks for watching!"
