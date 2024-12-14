SELECT i.name AS industry,
       EXTRACT(YEAR FROM f.date) AS year,
       SUM(f.amount_usd) AS total_funding
FROM funding_rounds f
JOIN startups s ON f.startup_id = s.startup_id
JOIN industries i ON s.industry_id = i.industry_id
GROUP BY i.name, year
ORDER BY i.name, year;

SELECT inv.name AS investor,
       SUM(f.amount_usd) AS total_invested
FROM investors inv
JOIN round_investors ri ON inv.investor_id = ri.investor_id
JOIN funding_rounds f ON f.round_id = ri.round_id
GROUP BY inv.name
ORDER BY total_invested DESC
LIMIT 10;

SELECT inv.name,
       COUNT(DISTINCT f.round_id) AS total_rounds,
       COUNT(DISTINCT EXTRACT(YEAR FROM f.date)) AS active_years,
       ROUND(COUNT(DISTINCT f.round_id)::DECIMAL /
             COUNT(DISTINCT EXTRACT(YEAR FROM f.date)), 2) AS avg_rounds_per_year
FROM investors inv
JOIN round_investors ri ON inv.investor_id = ri.investor_id
JOIN funding_rounds f ON f.round_id = ri.round_id
GROUP BY inv.name
ORDER BY avg_rounds_per_year DESC;

SELECT s.city,
       SUM(f.amount_usd) AS total_funding,
       COUNT(DISTINCT s.startup_id) AS startup_count
FROM startups s
JOIN funding_rounds f ON s.startup_id = f.startup_id
GROUP BY s.city
ORDER BY total_funding DESC;

WITH yearly AS (
    SELECT i.name AS industry,
           EXTRACT(YEAR FROM f.date) AS year,
           SUM(f.amount_usd) AS total
    FROM funding_rounds f
    JOIN startups s ON f.startup_id = s.startup_id
    JOIN industries i ON s.industry_id = i.industry_id
    GROUP BY i.name, year
)
SELECT industry,
       year,
       total,
       ROUND(
           (total - LAG(total) OVER (PARTITION BY industry ORDER BY year)) /
           NULLIF(LAG(total) OVER (PARTITION BY industry ORDER BY year),0) * 100, 2
       ) AS yoy_growth_pct
FROM yearly
ORDER BY industry, year;

SELECT s.name AS startup,
       SUM(f.amount_usd) AS total_funding
FROM startups s
JOIN funding_rounds f ON s.startup_id = f.startup_id
GROUP BY s.name
ORDER BY total_funding DESC
LIMIT 5;

SELECT ri1.investor_id AS investor_1,
       ri2.investor_id AS investor_2,
       COUNT(*) AS co_investments
FROM round_investors ri1
JOIN round_investors ri2 
  ON ri1.round_id = ri2.round_id AND ri1.investor_id < ri2.investor_id
GROUP BY ri1.investor_id, ri2.investor_id
ORDER BY co_investments DESC
LIMIT 10;

SELECT f.round_type,
       COUNT(f.round_id) AS num_rounds,
       SUM(f.amount_usd) AS total_funding
FROM funding_rounds f
GROUP BY f.round_type
ORDER BY total_funding DESC;

SELECT s.city,
       SUM(f.amount_usd) AS total_funding
FROM startups s
JOIN funding_rounds f ON s.startup_id = f.startup_id
GROUP BY s.city
ORDER BY total_funding DESC
LIMIT 5;

SELECT i.name AS industry,
       AVG(f.amount_usd) AS avg_funding
FROM startups s
JOIN industries i ON s.industry_id = i.industry_id
JOIN funding_rounds f ON s.startup_id = f.startup_id
GROUP BY i.name
ORDER BY avg_funding DESC;
