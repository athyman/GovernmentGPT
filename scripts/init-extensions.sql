-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Full-text search configuration for government documents
CREATE TEXT SEARCH CONFIGURATION government_english ( COPY = pg_catalog.english );
ALTER TEXT SEARCH CONFIGURATION government_english
    ALTER MAPPING FOR asciiword, asciihword, hword_asciipart,
                      word, hword, hword_part
    WITH unaccent, english_stem;