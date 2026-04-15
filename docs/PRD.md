# PRD — DataPeek
### Fast, minimal profiler for CSV & Parquet

---

## 1. Product Overview

**Name:** DataPeek  
**Type:** Single-page web app  

**Goal:**
> Understand a dataset in seconds.

**Core principles:**
- Fast  
- Minimal  
- Representative (not exhaustive)  
- Signal > noise  

---

## 2. Problem

Users frequently receive datasets and need a **quick first-pass understanding**:
- structure  
- data types  
- data quality  
- potential modeling signals  

Existing tools:
- too slow (heavy profiling)  
- too verbose (report overload)  
- too exploratory (not focused on orientation)  

---

## 3. Target Users

- Data scientists  
- Data analysts  
- Data engineers  
- Technical users handling ad hoc datasets  

---

## 4. Key Use Case

> “I just received this file — tell me what I’m looking at.”

---

## 5. MVP Scope

### Input
- Upload:
  - CSV  
  - Parquet  

### File Constraints
- Recommended max size: **≤ 50–100 MB**  
- Larger files: not optimized (acceptable limitation for MVP)  

---

## 6. Output (Single Page)

---

### 6.1 File Summary

- filename  
- file type (CSV / Parquet)  
- number of rows  
- number of columns  
- read time (ms)  

---

### 6.2 Signals / Warnings (Core Feature)

Heuristic-driven insights per column:

- possible ID column  
- mostly missing (>50%)  
- low variance column (top value ≥ 95%)  
- high cardinality text  
- likely categorical (low cardinality)  
- binary / potential target flag  
- suspicious mixed types  
- boolean disguised as string  

#### Binary / Potential Target

Flag if:
- exactly 2 unique values (excluding nulls)  
**OR**
- 2 dominant values covering ~100%  

Display with distribution:

> churn_flag → binary (1: 8.2%, 0: 91.8%)

---

#### Low Variance

- compute top value frequency ratio  
- flag if ≥ 0.95  
- ignore nulls  

Display:

> status → "active" (97.3%)

---

### 6.3 Column Overview Table

Per column:

- name  
- inferred dtype  
- non-null %  
- missing %  
- unique count  
- sample values (2–3)  

---

### 6.4 Numeric Summary

For numeric columns (int + float only):

- min  
- max  
- mean  
- median  

---

### 6.5 Data Preview

#### Primary:
**Random Sample**

- 10 rows  
- labeled: “Sample rows (random)”  

#### Interaction:
- 🔄 Resample button  

#### Secondary (collapsed):
- Head (first 5 rows)  
- Tail (last 5 rows)  

---

## 7. UX Structure

~~~
Upload
→ File Summary
→ Signals / Warnings
→ Column Overview
→ Sample Data
→ (Optional) Head & Tail
~~~

**UX principles:**
- single page  
- no tabs  
- minimal interaction  
- immediate rendering  
- clean hierarchy  

---

## 8. Heuristics Definitions

### Possible ID
- uniqueness ratio ≈ 1.0  
- column name contains: `id`, `key`, `code`  

---

### Mostly Missing
- missing > 50%  

---

### Low Variance
- top value frequency ≥ 0.95  

---

### Likely Categorical
- low cardinality relative to row count  

---

### High Cardinality Text
- high unique count  
- string dtype  

---

### Binary / Potential Target
- exactly 2 unique values  
**OR**  
- 2 dominant values  

---

### Boolean-like
- values resemble:
  - yes/no  
  - true/false  
  - 0/1  

---

### Mixed Types
- inconsistent parsing  
- numeric-like values inside string columns  

---

## 9. Technical Design

### Stack

- **Backend:** Robyn  
- **Processing:** Polars  
- **Templating:** Jinja2  
- **Frontend:** HTML + minimal CSS (+ optional HTMX)  

---

### Folder Structure

~~~
app/
  main.py
  routes/
    home.py
    profile.py
  services/
    file_reader.py
    profiler.py
    heuristics.py
  templates/
    base.html
    home.html
    profile.html
  static/
    styles.css
~~~

---

### Processing Flow

1. Upload file  
2. Detect format (CSV / Parquet)  
3. Load with Polars  
4. Compute:
   - schema  
   - null counts  
   - unique counts  
   - top value stats  
5. Apply heuristics  
6. Generate preview:
   - sample (random)  
   - head/tail  
7. Render via Jinja template  

---

### CSV Handling (MVP Assumptions)

- delimiter: auto or default comma  
- header: assumed present  
- parsing fallback: string if needed  

---

### Sampling Strategy

- full dataset loaded (within size constraint)  
- random sample:

~~~python
df.sample(n=10, seed=42)
~~~

---

## 10. Performance Principles

- compute only essential stats  
- reuse aggregates across heuristics  
- avoid full distributions  
- keep preview small (10 rows)  
- optimize for perceived speed  

---

## 11. UI Constraints

- truncate long text (~50 chars)  
- horizontal scroll for wide tables  
- simple tables (no sorting/filtering)  

---

## 12. Error Handling (Minimal)

- unsupported file → message  
- parsing failure → fallback / error  
- empty file → message  

---

## 13. Non-Goals (Strict)

- correlations  
- charts / histograms  
- pairwise analysis  
- filtering / sorting UI  
- pagination  
- authentication  
- persistence  
- full EDA reports  

---

## 14. Success Criteria

- dataset understood in <10 seconds  
- key signals visible immediately  
- UI is clean and uncluttered  
- app feels fast and responsive  

---

## 15. Future Extensions

- top values for categorical columns  
- markdown export  
- schema comparison  
- drift detection  
- join key suggestions  
- RAG integration  

---

## 16. Positioning

> DataPeek is not an EDA tool.  
> It is a **first-contact data profiler**.

---

## 17. Build Scope

- achievable in **1–2 focused sessions**  
- no infrastructure complexity  
- ideal for learning **Robyn + Polars + Jinja2** through a real use case  