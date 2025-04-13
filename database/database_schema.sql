CREATE TABLE IF NOT EXISTS stock_details (
    "symbol" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT,
    "country" TEXT,
    "ipo_year" INTEGER,
    "volume" INTEGER,
    "sector" TEXT,
    "industry" TEXT
);

CREATE TABLE IF NOT EXISTS etf_details (
    "symbol" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT
);

CREATE TABLE IF NOT EXISTS stock_timeseries (
    "symbol" TEXT REFERENCES stock_details(symbol),
    "date" DATE,
    "price_open" FLOAT,
    "price_close" FLOAT,
    "price_low" FLOAT,
    "price_high" FLOAT,
    "volume" INTEGER
);

CREATE TABLE IF NOT EXISTS etf_timeseries (
    "symbol" TEXT REFERENCES etf_details(symbol),
    "date" DATE,
    "price_open" FLOAT,
    "price_close" FLOAT,
    "price_low" FLOAT,
    "price_high" FLOAT,
    "volume" INTEGER
);

