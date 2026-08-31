AI Product Catalog & Price List Assistant

An AI-assisted workflow that converts supplier PDF and Excel price lists into structured, validated product data and routes uncertain records for human review before export.

1. Problem

E-commerce and website administrators often receive supplier product and price-list files that contain inconsistent formats, missing fields, duplicate or near-duplicate products, and ambiguous values.

The manual workflow requires:

Opening the supplier document

Identifying fields such as product name, brand, UOM, MOQ, price, and HSN

Copying the values into a structured spreadsheet

Normalizing formatting and UOMs

Checking missing or suspicious values

Reviewing exceptions

Preparing the final dataset for website/e-commerce use

A controlled manual benchmark using 50 synthetic product records took 20 minutes (approximately 24 seconds per product).

2. Solution

The AI Product Catalog & Price List Assistant turns that workflow into a repeatable browser-based process:

Upload -> Extract -> Validate -> Review -> Export

The system uses Gemini for document understanding and Python validation rules for deterministic business checks.

Uncertain information is flagged for human review rather than guessed.

3. Key Features

Upload supplier PDF, XLSX, or XLS files

AI extraction using Google Gemini

Structured product schema

UOM normalization

Price normalization

Missing-field detection

Invalid-value checks

Potential duplicate / near-duplicate detection

Human-review flags with reasons

All / Valid / Needs Review filters

Processing-time measurement

Operational logging

Gemini quota/rate-limit error handling

Excel export

Non-developer web interface

4. Product Schema

Each extracted record contains:

Field

Description

Product Name

Supplier product name

Brand

Product brand

UOM

Unit of measure

MOQ

Minimum order quantity

Price

Product price

HSN

HSN code

Validation metadata:

Field

Description

needs_review

Whether human review is required

review_reason

Reason for the review flag

Missing or uncertain values are represented as null where appropriate.

5. Architecture

Supplier PDF / Excel
        |
        v
React + TypeScript UI
        |
        v
FastAPI backend
        |
        v
File parsing
  |             |
  |             +--> Excel -> pandas/openpyxl
  |
  +--> PDF -> pypdf
        |
        v
Google Gemini
        |
        v
Structured product schema
        |
        v
Python validation
        |
        v
Human review flags
        |
        v
React results
        |
        v
XLSX export

The AI extraction layer and deterministic validation layer are intentionally separated. Gemini interprets the source document; Python applies explicit business rules.

6. Technology Stack

Frontend: React + TypeScript

Backend: Python + FastAPI

AI: Google Gemini API (gemini-3.6-flash)

PDF: pypdf

Excel: pandas + openpyxl

Validation: Python

Output: XLSX

Storage: Local processing for the current version

Configuration: .env

7. Project Structure

ai-product-catalog-assistant/
|
+-- app/
|   +-- __init__.py
|   +-- extraction.py
|   +-- logging_config.py
|   +-- main.py
|   +-- schemas.py
|   +-- validation.py
|
+-- frontend/
|   +-- src/
|   +-- public/
|   +-- package.json
|   +-- ...
|
+-- sample-data/
+-- evaluation_cases/
+-- test_extraction.py
+-- test_gemini.py
+-- test_validation.py
+-- requirements.txt
+-- .env.example
+-- .gitignore
+-- README.md

8. Setup

Prerequisites

Python

Node.js and npm

A Gemini API key

Backend setup

From the project root:

python -m venv .venv

Activate the environment on Windows PowerShell:

.venv\Scripts\Activate.ps1

Install Python dependencies:

pip install -r requirements.txt

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here

Do not commit the real .env file.

Frontend setup

From the project root:

cd frontend
npm install

9. Run the Application

Terminal 1 - Backend

From the project root:

.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

Backend:

http://127.0.0.1:8000

Health check:

http://127.0.0.1:8000/health

Terminal 2 - Frontend

From the project root:

cd frontend
npm run dev

Frontend:

http://localhost:5173

10. How to Use

Open http://localhost:5173

Upload a supplier PDF or Excel file

Click Process supplier file

Review the processing summary

Use All, Valid, or Needs review filters

Review flagged records and reasons

Click Download Excel

No direct interaction with Python, FastAPI, or Gemini is required from the end user.

11. Validation Behavior

The system is designed around a human-in-the-loop workflow.

Missing value

If price, HSN, or MOQ is missing:

Value = null
Needs review = true

The system does not invent the missing value.

UOM variation

Inputs such as:

PCS
pcs
Nos
Piece

can be normalized to the canonical UOM used by the workflow.

Duplicate / near-duplicate

Potentially duplicated records are flagged for human review instead of being silently removed.

Ambiguous value

If the system cannot confidently determine a value, it is routed to human review.

12. Evaluation

A controlled set of 10 evaluation scenarios was used:

Complete normal product

Missing price

Missing HSN

Missing MOQ

Duplicate / near-duplicate product

UOM variation

Product-name variation

Price formatting

Multiple brands in one file

Ambiguous / unreadable value

Final result

10/10 test cases passed

Pass rate: 100%

13. Performance Evidence

Manual baseline

50 products -> 20 minutes

Approximately:

24 seconds per product

Automated benchmark

51 products -> 49.43 seconds backend processing time

Result:

51 products extracted

46 valid

5 requiring human review

Review rate:

5 / 51 = approximately 9.8%

The automated and manual benchmarks use 51 and 50 records respectively, so the timing comparison is indicative rather than a perfectly identical workload comparison.

14. Reliability and Failure Handling

Operational logs record:

Processing start

File name and file type

File size

AI extraction completion

Product count

Valid/review counts

Processing duration

API failures

Unexpected failures

Failure: Duplicate over-flagging

The initial duplicate rule flagged 33 of 51 records.

The validation logic was tightened to require stronger evidence of duplication.

Result:

33 review flags -> 5 legitimate review records

Failure: Gemini quota exhaustion

During evaluation, Gemini returned HTTP 429 RESOURCE_EXHAUSTED because the free-tier request quota was exceeded.

The initial user-facing message was too generic.

The backend was updated to distinguish quota/rate-limit failures and show a specific message explaining that the AI service request limit had been reached.

Failure: Development-time syntax regression

A temporary SyntaxError: unmatched ')' occurred while modifying the FastAPI backend.

The issue was corrected and the backend was restarted and verified successfully.

15. Privacy and Configuration

API credentials are stored through environment configuration.

The real .env file is excluded from version control.

.env.example contains only a placeholder key.

Current processing is local.

The application does not automatically publish supplier data to a production website.

16. Non-Goals

The current version does not:

Automatically publish products to a production website

Autonomously approve uncertain supplier information

Act as a generalized business agent

Provide a complex enterprise dashboard

Claim universal extraction accuracy across all supplier formats

17. Limitations

The current evaluation uses synthetic data because a live supplier feed and live target user were unavailable during the sprint.

The 100% evaluation result applies to the defined 10-case evaluation set and should not be interpreted as universal production accuracy.

AI-service availability can be affected by external Gemini quota limits.

Human review remains necessary for uncertain information.

The current architecture uses local processing and is intended as an initial working version.

18. Next Two-Week Plan

During the first two weeks of real usage, the following metrics should be tracked:

Processing time per supplier file

Field accuracy

Human-review rate

Manual correction rate

Number of supplier files processed

User-reported friction

Frequency of AI/API failures

The next iteration should prioritize changes based on observed review patterns, supplier document variation, and user feedback.

19. Project Outcome

The project transforms a repetitive supplier data-processing workflow into a measurable human-in-the-loop system:

Manual processing -> AI-assisted extraction -> deterministic validation -> human review -> structured export

The system is designed to reduce repetitive work while keeping uncertain decisions visible and controlled.