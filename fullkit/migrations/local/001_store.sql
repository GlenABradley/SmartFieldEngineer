CREATE TABLE store_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    home_id TEXT NOT NULL,
    store_instance_id TEXT NOT NULL,
    active INTEGER NOT NULL CHECK (active IN (0, 1)),
    recovery INTEGER NOT NULL CHECK (recovery IN (0, 1)),
    CHECK (recovery = 0 OR active = 0)
);
CREATE TABLE schema_history (
    version INTEGER PRIMARY KEY,
    sha256 TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    operation_id TEXT NOT NULL UNIQUE
);
CREATE TABLE maintenance_receipts (
    operation_id TEXT PRIMARY KEY,
    command TEXT NOT NULL,
    state TEXT NOT NULL CHECK (state = 'confirmed'),
    result_json TEXT NOT NULL,
    completed_at TEXT NOT NULL
);
