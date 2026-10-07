-- created an index on the repos table to improve search performance for repo names (case-insensitive)

CREATE UNIQUE INDEX repos_idx_lower ON repos(lower(repo_name), owner_id);