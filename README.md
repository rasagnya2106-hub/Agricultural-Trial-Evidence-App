# 🌱 Agricultural Trial Evidence App

An evidence-focused application for searching agricultural trial records, comparing trial results, and tracing findings back to their original source records.

The application is designed around a simple business problem: agricultural trial data is often spread across spreadsheets and reports, with inconsistent product names, crop names, units, duplicate records, missing values, and conflicting results.

This application imports those records, normalizes them, preserves original evidence, provides structured search and comparison, and includes an LLM-powered evidence agent with tool-based access to the trial database.

---

## 1. Business Understanding

The client has hundreds of agricultural crop trials stored across spreadsheets and reports.

The main challenges are:

- Inconsistent product names such as `Harvest Plus`, `HarvestPlus`, and `HARVESTPLUS`
- Inconsistent crop names such as `Potato` and `potatoes`
- Different country representations such as `FR`, `DE`, and `ES`
- Different measurement units such as `t/ha` and `kg/ha`
- Duplicate trial records across spreadsheets and reports
- Missing values
- Conflicting values between different source documents
- Difficulty tracing a result back to the original evidence

The application addresses these problems by creating a normalized trial dataset while preserving all original source records.

Users can then:

1. Search trials using crop, product, country, year, and trial type.
2. Compare treatment and control results.
3. Inspect original source records.
4. Ask natural-language questions through an evidence agent.

---

## 2. Main Features

### Trial Ingestion

The application imports:

- `trials_a.csv`
- `trials_b.csv`
- Text-based trial reports

### Data Normalization

The ingestion process normalizes:

- Product names
- Crop names
- Country codes
- Measurement units

Examples:

- `HarvestPlus` → `Harvest Plus`
- `RootBoost` → `Root Boost`
- `potatoes` → `Potato`
- `FR` → `France`
- `DE` → `Germany`
- `ES` → `Spain`
- `t/ha` → `kg/ha`

### Duplicate Handling

Duplicate source records are not blindly discarded.

The application maintains:

- A normalized trial record for retrieval
- Original source records for evidence traceability

This allows multiple sources to remain connected to the same trial.

### Conflict Handling

Conflicting source values are preserved.

For example, trial `T03` has:

- `T03_summary.txt` → 44,000 kg/ha treatment yield
- `trials_a.csv` → 42,000 kg/ha treatment yield

The application does not silently choose one value as the final truth.

Instead, both original source records remain available for inspection.

### Missing Values

Missing values are represented as missing rather than zero.

For example, trial `T05` contains a treatment yield but no reported control yield.

The application therefore does not calculate an artificial treatment-control difference.

### Trial Comparison

The application calculates:

- Treatment yield
- Control yield
- Absolute difference
- Percentage change when the control value is available

### Evidence Source Inspection

Users can enter a trial ID such as `T03` and inspect all original source records associated with that trial.

### Natural-Language Evidence Agent

The application includes an LLM-powered agent that can select tools for retrieving agricultural trial evidence.

Available tools:

- `search_trials`
- `compare_trials`
- `find_evidence`
- `get_trial_sources`

Tool activity is captured so that the agent's actions can be inspected.

---

## 3. Architecture

```text
CSV Files + Trial Reports
          |
          v
      Ingestion
          |
          v
     Normalization
          |
          +----------------------+
          |                      |
          v                      v
   Normalized Trials       Original Sources
          |                      |
          +----------+-----------+
                     |
                     v
                  SQLite
                     |
          +----------+-----------+
          |                      |
          v                      v
    Deterministic Tools      Evidence Agent
          |                      |
          |                  Gemini LLM
          |                      |
          +----------+-----------+
                     |
                     v
                Streamlit UI
```

---

## 4. Technology Stack

### Python

Main application language.

### Streamlit

Used to provide the browser-based interface.

### SQLite

Used as the local relational database for normalized trials and original source records.

### Pandas

Used during data ingestion and processing of CSV-based trial data.

### Pydantic

Used for structured trial data models.

### Google Gemini

Used for the natural-language evidence agent and tool selection.

### Python-dotenv

Used to load the Gemini API configuration from `.env`.

---

## 5. Database Design

The application uses two main tables.

### `trials`

Contains the normalized trial records used for searching and comparison.

Important fields include:

- Trial ID
- Crop
- Product
- Country
- Year
- Trial type
- Treatment yield
- Control yield
- Source
- Notes

### `trial_sources`

Stores the original source records associated with each trial.

This table allows the application to preserve:

- Duplicate source records
- Different source values
- Source-specific notes
- Original source type

This design separates the normalized retrieval layer from the evidence/audit layer.

---

## 6. Why SQLite Instead of Vector Search?

The initial client questions are primarily structured queries such as:

- Crop = Wheat
- Product = Harvest Plus
- Country = France
- Year = 2024
- Trial Type = Scientific

For these exact filters, SQL provides deterministic and auditable retrieval.

A vector database was therefore not necessary for the first milestone.

A future version could add semantic/vector search for more complex natural-language questions across the unstructured report content.

---

## 7. Agent Design

The agent uses tools rather than directly generating trial facts.

The general flow is:

```text
User Question
      |
      v
Gemini Agent
      |
      v
Select Appropriate Tool
      |
      v
Python Tool
      |
      v
SQLite Database
      |
      v
Evidence Result
      |
      v
Agent Response
```

Examples:

### Listing Question

```text
Show all wheat trials involving Harvest Plus
```

The agent can use:

```text
search_trials
```

### Evidence Question

```text
What evidence supports Root Boost improving potato yields?
```

The agent can use:

```text
find_evidence
```

### Source Verification

```text
Show the original evidence for T03
```

The agent can use:

```text
get_trial_sources
```

### Comparison

```text
Compare T01 and T02
```

The agent can use:

```text
compare_trials
```

The separation between the agent and deterministic tools reduces the risk of the model inventing database values.

---

## 8. Data Quality Checks

The application explicitly handles several data-quality scenarios.

### Inconsistent Names

Normalized to a common representation.

### Different Units

Yields are converted to kg/ha.

### Duplicate Records

Duplicate source records are retained for traceability while normalized trial records are consolidated.

### Conflicting Values

Conflicting source values are preserved and exposed for review.

### Missing Values

Missing treatment/control values remain missing.

### Unsupported Questions

If the supplied dataset contains no relevant evidence, the application should report that no matching evidence was found rather than inventing a result.

---

## 9. Evaluation

A six-check evaluation was implemented in `evaluation.py`.

The current evaluation result is:

```text
[PASS] Wheat + Harvest Plus search
[PASS] Scientific wheat trial filter
[PASS] Trial comparison calculations
[PASS] T03 conflicting source values preserved
[PASS] Missing control value handled correctly
[PASS] No unsupported rice evidence

RESULT: 6/6 checks passed
```

The evaluation covers:

1. Search correctness
2. Trial-type filtering
3. Comparison calculations
4. Conflict preservation
5. Missing-value handling
6. Unsupported evidence handling

---

## 10. Example Trial Evidence

### T01

- Crop: Wheat
- Product: Harvest Plus
- Country: France
- Year: 2023
- Trial type: Scientific
- Treatment: 8,400 kg/ha
- Control: 8,000 kg/ha

### T02

- Crop: Wheat
- Product: Harvest Plus
- Country: Germany
- Year: 2024
- Trial type: Demonstration
- Treatment: 7,800 kg/ha
- Control: 7,500 kg/ha

### T03

- Crop: Potato
- Product: Root Boost
- Country: Spain
- Year: 2023
- Trial type: Demonstration
- Normalized treatment value: 42,000 kg/ha
- Control: 40,000 kg/ha
- Original sources contain conflicting treatment values.

### T04

- Crop: Potato
- Product: Root Boost
- Country: France
- Year: 2024
- Trial type: Scientific
- Treatment: 45,000 kg/ha
- Control: 45,000 kg/ha

### T05

- Crop: Wheat
- Product: Harvest Plus
- Country: Germany
- Year: 2025
- Trial type: Demonstration
- Treatment: 8,100 kg/ha
- Control: Not reported

### T06

- Crop: Wheat
- Product: Harvest Plus
- Country: Spain
- Year: 2021
- Trial type: Scientific
- Treatment: 6,600 kg/ha
- Control: 6,000 kg/ha

---

## 11. Project Structure

```text
Agricultural-Trial-Evidence-App/
│
├── data/
├── sample-data/
├── venv/
│
├── .env
├── .gitignore
│
├── agent.py
├── app.py
├── database.py
├── data_processing.py
├── evaluation.py
├── ingestion.py
├── models.py
├── normalization.py
├── tools.py
├── test_tools.py
├── test_gemini.py
├── test_chat.py
│
├── requirements.txt
└── README.md
```

---

## 12. Setup

### Create and Activate the Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Gemini

Create a `.env` file:

```text
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

Do not commit the actual API key to source control.

### Run the Application

```bash
streamlit run app.py
```

The application will open in the browser at the local Streamlit URL.

---

## 13. Run Evaluation

Run:

```bash
python evaluation.py
```

The evaluation script checks the core evidence and data-quality behavior.

Expected result:

```text
RESULT: 6/6 checks passed
```

---

## 14. Testing the Tools

The tool tests can be run with:

```bash
python test_tools.py
```

These tests cover:

- Trial search
- Trial comparison
- Evidence retrieval
- Original source retrieval

---

## 15. Assumptions

The following assumptions were made for the first milestone:

1. Trial IDs are the primary identifier for linking records across sources.
2. Product and crop spelling variations refer to the same product/crop when they match the supplied normalization rules.
3. `FR`, `DE`, and `ES` represent France, Germany, and Spain.
4. `t/ha` is converted to `kg/ha` using 1 t/ha = 1,000 kg/ha.
5. Missing values are not treated as zero.
6. Conflicting source values are preserved instead of automatically selecting a final value.
7. The supplied files are treated as the available evidence set for this prototype.

---

## 16. Limitations

This is a prototype focused on the supplied agricultural trial data.

Current limitations include:

- The application only covers the supplied sample data.
- Semantic search across report text is not yet implemented.
- Authentication is not implemented.
- Production deployment is outside the current scope.
- Mobile data capture is outside the current scope.
- Multilingual support is outside the current scope.
- Statistical significance cannot be inferred when it is not documented in the supplied evidence.
- Conflicting source values require human review rather than automatic resolution.
- LLM availability and API quota can affect the natural-language agent.

---

## 17. Future Improvements

Potential next milestones include:

1. Add semantic/vector search for unstructured reports.
2. Add a human-in-the-loop review workflow for conflicting evidence.
3. Add richer evidence citations in agent responses.
4. Add automated data-quality reports.
5. Add additional trial metadata and filtering.
6. Add persistent evaluation datasets and regression tests.
7. Add production authentication and deployment when required.

---

## 18. Out of Scope

The following were intentionally not implemented because they were outside the supplied assignment scope:

- Production integrations
- Authentication
- Mobile capture
- Multilingual support
- Production deployment

---

## 19. Model Configuration

The application reads the Gemini API key from the environment:

```text
GEMINI_API_KEY
```

The API credential itself should never be committed to the repository.

The agent model configuration is defined in `agent.py`.

---

## 20. Key Design Principle

The central design principle is:

> Use the LLM to decide which evidence-retrieval action to take, but use deterministic tools and the database for factual trial retrieval and calculations.

This keeps the evidence layer inspectable and makes the system easier to test and evaluate.
