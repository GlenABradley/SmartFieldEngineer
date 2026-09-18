CREATE TABLE audit (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT NOT NULL UNIQUE,
    command TEXT NOT NULL,
    principal TEXT NOT NULL,
    at TEXT NOT NULL,
    data_json TEXT NOT NULL
);
CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    created_seq INTEGER NOT NULL UNIQUE REFERENCES audit(seq),
    summary_json TEXT NOT NULL
);
CREATE TABLE job_events (
    seq INTEGER PRIMARY KEY REFERENCES audit(seq),
    job_id TEXT NOT NULL REFERENCES jobs(job_id),
    payload_json TEXT NOT NULL
);
CREATE TABLE operations (
    operation_id TEXT PRIMARY KEY REFERENCES audit(operation_id),
    fingerprint TEXT NOT NULL,
    receipt_json TEXT NOT NULL
);
