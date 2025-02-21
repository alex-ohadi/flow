CREATE TABLE IF NOT EXISTS datas (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

SELECT 'Datas table setup for database Data!' AS result;
