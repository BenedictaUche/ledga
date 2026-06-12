# Ledga
### BaaS Back-Office Agent for Informal African SMBs

Ledga is an agentic Business-as-a-Service platform that runs the back-office
for informal small businesses — pharmacies, supermarkets, and provision stores
— without requiring owners to learn any software.

A single operator manages multiple shops simultaneously. Shop owners simply send
a plain-text message describing what happened during the day. Ledga's AI agents
parse, record, reconcile, and flag exceptions. The operator reviews alerts in a
real-time dashboard. At end of day, every owner gets a plain-language summary
of their sales, profit, and outstanding credit.

Built for the UiPath AgentHack — Track 2: UiPath Maestro BPMN.

---

## The Problem

Tens of millions of informal small businesses across Africa run entirely on
memory and guesswork. Owners don't know their real profit, can't track who owes
them money, and have no visibility into stock until shelves are empty. Existing
tools assume users think like software users. They don't get adopted.

---

## The Solution

An agentic BaaS platform where one operator manages the back-office for
multiple informal SMBs simultaneously. No shop owner ever logs into software.

**How it works:**
1. Shop owner sends a plain message: *"sold para x20, Mama Chioma took ₦3,500 credit"*
2. LLM agent parses the message into structured transaction data
3. Python backend calculates profit, updates inventory, tracks credit
4. Exceptions (low stock, overdue credit, large credit) are flagged automatically
5. Operator reviews and resolves exceptions in the Angular dashboard
6. UiPath Maestro BPMN orchestrates the full daily flow from open to close
7. End of day — owner receives a plain-language summary

---

## UiPath Components Used

- **UiPath Maestro BPMN** — orchestrates the full business day process:
  Open → Receive Message → Parse → Update Records → Exception Handling → Close
- **UiPath Agent Builder** — governs exception routing and human checkpoints
- **UiPath Action Center** — operator human-in-the-loop tasks for exception review
- **UiPath Automation Cloud** — deployment and orchestration platform

The BPMN process file is included in this repo: `LedgaBusinessDay.bpmn`

---

## Coding Agents Used

This solution was built using **Claude** (claude.ai) and **Claude Code** as
coding agents throughout development:
- BPMN process definition generated with Claude
- Python backend architecture designed with Claude
- UiPath integration layer built with Claude Code
- Database schema and seed data generated with Claude

---

## Tech Stack

**Backend**
- Python FastAPI
- Anthropic Claude API (LLM transaction parser)
- Supabase (PostgreSQL - multi-tenant data layer)
- UiPath Automation Cloud API

**Frontend**
- Angular 19
- TypeScript
- SCSS
- Supabase JS client

**Orchestration**
- UiPath Maestro BPMN
- UiPath Action Center (human-in-the-loop)

---

## Architecture

Shop Owner (plain text message) -> Operator Dashboard (Angular) -> Python FastAPI Backend -> LLM Parser (Claude) → Structured JSON -> Supabase (transactions, inventory, credit ledger) -> Exception Detection → UiPath Action Center (human checkpoint) -> UiPath Maestro BPMN (orchestrates full daily flow) -> End-of-Day Summary → Shop Owner

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Operator | operator@ledga.io | demo1234 |

**Demo shops (pre-seeded):**
- Adunni Pharmacy — active, daily transactions
- Chukwu Supermarket — exception state (low stock + overdue credit)
- Fatima Provisions — active, no exceptions

---

## Setup Instructions

### Prerequisites
- Python 3.11
- Node.js 18+
- Angular CLI 19
- Supabase account
- Anthropic API key
- UiPath Automation Cloud account

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Fill in your keys
uvicorn main:app --reload
```

**Environment variables required:**

SUPABASE_URL=your_supabase_project_url

SUPABASE_SERVICE_KEY=your_supabase_service_role_key

ANTHROPIC_API_KEY=your_anthropic_api_key

UIPATH_BASE_URL=https://staging.uipath.com

UIPATH_ACCOUNT=your_account_name

UIPATH_TENANT=your_tenant_name

UIPATH_TOKEN=your_personal_access_token

### Database

Run `schema.sql` in your Supabase SQL editor to create all tables.
Run the seed queries from the README to populate demo data.

### Frontend

```bash
cd frontend
npm install
cp src/environments/environment.example.ts src/environments/environment.ts
# Fill in your Supabase URL and anon key in environment.ts
ng serve
```

Open `http://localhost:4200`

### UiPath

Import `LedgaBusinessDay.bpmn` into UiPath Studio and publish to your
Automation Cloud tenant.

---

## Project Structure

### Database

Run `schema.sql` in your Supabase SQL editor to create all tables.
Run the seed queries from the README to populate demo data.

### Frontend

```bash
cd frontend
npm install
cp src/environments/environment.example.ts src/environments/environment.ts
# Fill in your Supabase URL and anon key in environment.ts
ng serve
```

Open `http://localhost:4200`

### UiPath

Import `LedgaBusinessDay.bpmn` into UiPath Studio and publish to your
Automation Cloud tenant.

---

## License

MIT
