CREATE TABLE industries (
    industry_id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE startups (
    startup_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    industry_id INT REFERENCES industries(industry_id),
    city VARCHAR(100),
    state VARCHAR(100),
    founded_year INT
);

CREATE TABLE investors (
    investor_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    investor_type VARCHAR(50) DEFAULT 'VC'  -- optional
);

CREATE TABLE funding_rounds (
    round_id SERIAL PRIMARY KEY,
    startup_id INT REFERENCES startups(startup_id),
    round_type VARCHAR(50),
    amount_usd NUMERIC(12,2),
    date DATE
);

CREATE TABLE round_investors (
    round_id INT REFERENCES funding_rounds(round_id),
    investor_id INT REFERENCES investors(investor_id),
    PRIMARY KEY (round_id, investor_id)
);
