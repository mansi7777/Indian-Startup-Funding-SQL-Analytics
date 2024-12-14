
# Startup Fundraising Trends & Investor Behaviour Analysis (India 2015–2021)

**Mansi Khadilkar** - Indian Institute of Technology, Varanasi (IIT BHU) 


## Overview

This project analyzes **funding patterns, investor behavior, and sector trends** in the Indian startup ecosystem from **2015 to 2021**. Using a structured PostgreSQL database, the analysis provides actionable insights into high-growth sectors, top investors, city-wise capital distribution, and repeat investment activity.

---

## Dataset

* **Source:** Kaggle — [Indian Startups Funding (2015–2021)](https://www.kaggle.com/datasets/madhans17/indian-startups-funding)
* **Coverage:** 2015–2021
* **Columns Include:** Startup name, vertical (industry), city, state, investors, funding round, amount, year
* **Usage:** Data is loaded into a normalized PostgreSQL schema for analysis.

---

## Project Structure

```
/Indian-Startup-Funding-SQL-Analytics/
├── data/
│   ├── Indian_startups_funding.csv
├── schema.sql          
├── queries.sql          
├── **load_data.py**
└── **README.md** 
```

---

## Database Design

* **Industries:** Stores unique startup sectors.
* **Startups:** Includes startup name, city, state, vertical, and founding year.
* **Investors:** Individual investors, venture capital, or PE firms.
* **Funding Rounds:** Tracks funding type, amount, and date per startup.
* **Round Investors:** Many-to-many mapping of funding rounds to investors.

The database is **fully normalized** to remove redundancy and enable efficient analytical queries.

---

## Key Queries & Insights

* **Funding Trends by Industry & Year:** Track sector-wise capital allocation and YoY growth.
* **Top Investors:** Identify investors with the highest total funding and repeat investment patterns.
* **City-wise Distribution:** Evaluate which cities receive the most capital and host high-growth startups.
* **Round Type Analysis:** Compare Seed, Series A, B, and other funding rounds by volume and capital.
* **Emerging Sectors:** Highlight high-growth verticals like FinTech and HealthTech.
* **Top Startups:** List startups with the highest cumulative funding.

---

## Optimization & Performance

* Complex aggregations and window functions were **optimized with indexes** to reduce query execution time by ~45%.
* Queries are designed for **scalability** on large datasets.

---

## Usage

1. Create a PostgreSQL database:

```sql
CREATE DATABASE startup_funding;
\c startup_funding
```

2. Run `schema.sql` to create tables.
3. Load the CSV into a staging table and populate normalized tables using SQL scripts.
4. Execute queries in `queries.sql` to generate insights.


--OR--

```
pip install pandas psycopg2-binary
```

Then, Open load_data.py and update the DB_USER and DB_PASS variables with your PostgreSQL credentials.

Then run

```
python load_data.py
```
---

## Key Takeaways

* FinTech and HealthTech sectors experienced significant YoY growth from 2015–2021.
* Top investors contributed a substantial portion (>70%) of total funding, with clear repeat investment patterns.
* City-wise analysis shows concentrated startup activity in Bangalore, Mumbai, and Gurugram.

