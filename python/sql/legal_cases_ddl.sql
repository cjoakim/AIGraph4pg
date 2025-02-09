-- Delete/Define the legal_cases table and its' related indexes.

SET search_path TO public;

DROP TABLE IF EXISTS legal_cases CASCADE;

CREATE TABLE legal_cases (
    id                   bigserial primary key,
    name                 VARCHAR(1024),
    name_abbreviation    VARCHAR(1024),
    case_url             VARCHAR(1024),
    decision_date        DATE,
    court_name           VARCHAR(1024),
    citation_count       INTEGER,
    text_data            TEXT,
    json_data            JSONB,
    embedding            vector(1536)
);

DROP INDEX IF EXISTS idx_legal_cases_name_abbreviation;
CREATE INDEX idx_legal_cases_name_abbreviation
ON legal_cases(name_abbreviation);

DROP INDEX IF EXISTS idx_legal_cases_decision_date;
CREATE INDEX idx_legal_cases_decision_date
ON legal_cases(decision_date);

DROP INDEX IF EXISTS idx_legal_cases_court_name;
CREATE INDEX idx_legal_cases_court_name
ON legal_cases(court_name);

DROP INDEX IF EXISTS idx_legal_cases_citation_count;
CREATE INDEX idx_legal_cases_citation_count
ON legal_cases(citation_count);

DROP INDEX IF EXISTS idx_legal_cases_json_data_gin;
CREATE INDEX idx_legal_cases_json_data_gin
ON legal_cases USING gin (json_data);

-- create a diskann index by using Cosine distance operator
-- See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-use-pgdiskann
DROP INDEX IF EXISTS idx_legal_cases_diskann_embedding;
CREATE INDEX idx_legal_cases_diskann_embedding
ON legal_cases
USING diskann (embedding vector_cosine_ops);


-- The following commented-out lines relate to creating a vector index
-- with the pg vector extension. This is an alternative to the diskann.

-- Delete/Define the idx_legal_cases_ivfflat_embedding index.
-- See https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/how-to-optimize-performance-pgvector#indexing
-- Set ivfflat.probes to 1/10th the value of lists
-- Set lists to ~ rows/1000

-- SET ivfflat.probes = 5;
-- DROP INDEX IF EXISTS idx_legal_cases_ivfflat_embedding;
-- CREATE INDEX idx_legal_cases_ivfflat_embedding
-- ON     legal_cases
-- USING  ivfflat (embedding vector_cosine_ops)
-- WITH  (lists = 50);
