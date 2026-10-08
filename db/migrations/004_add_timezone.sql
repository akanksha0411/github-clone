-- Added a new column 'created_at' to the 'repos' table to store the timestamp of when a repository is created. The default value is set to the current timestamp and it cannot be null.
BEGIN;
ALTER TABLE repos ADD COLUMN created_at TIMESTAMPTZ DEFAULT now() NOT NULL;

-- Edited the 'created_at' column in the 'versions' table to use TIMESTAMPTZ (timestamp with time zone) instead of TIMESTAMP. This change ensures that the timestamp is stored with time zone information, which is important for applications that may be used across different time zones. The existing data in the 'created_at' column will be converted to TIMESTAMPTZ.

ALTER TABLE versions 
ALTER COLUMN created_at TYPE TIMESTAMPTZ,
ALTER COLUMN created_at SET NOT NULL;

ALTER TABLE sessions
ALTER COLUMN created_at TYPE TIMESTAMPTZ,
ALTER COLUMN created_at SET NOT NULL;
COMMIT;



