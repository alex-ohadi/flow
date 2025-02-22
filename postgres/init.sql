CREATE TABLE IF NOT EXISTS datas (
    id SERIAL PRIMARY KEY,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    matched_data JSONB NOT NULL
);

SELECT 'Datas table setup for database Data!' AS result;
