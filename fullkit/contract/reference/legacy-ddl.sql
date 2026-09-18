
        CREATE TABLE IF NOT EXISTS office_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, data TEXT NOT NULL, version INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), kind TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), hash TEXT NOT NULL, name TEXT NOT NULL, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS reservations(job TEXT PRIMARY KEY REFERENCES jobs(id), start TEXT NOT NULL, end TEXT NOT NULL, state TEXT NOT NULL, review TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), version INTEGER NOT NULL, data TEXT NOT NULL, hash TEXT NOT NULL, expires TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT);
        CREATE TABLE IF NOT EXISTS stock(sku TEXT NOT NULL, location TEXT NOT NULL, qty INTEGER NOT NULL, unit_cents INTEGER NOT NULL, PRIMARY KEY(sku,location));
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), kind TEXT NOT NULL, data TEXT NOT NULL, hash TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS serial_observations(id TEXT PRIMARY KEY, data TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS serial_assignments(observation TEXT PRIMARY KEY REFERENCES serial_observations(id), job TEXT NOT NULL REFERENCES jobs(id), asset TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS asset_heads(asset TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS asset_bindings(id TEXT PRIMARY KEY, asset TEXT NOT NULL REFERENCES asset_heads(asset), revision INTEGER NOT NULL, observation TEXT UNIQUE NOT NULL REFERENCES serial_assignments(observation), data TEXT NOT NULL, UNIQUE(asset,revision));
        CREATE TABLE IF NOT EXISTS asset_jobs(asset TEXT REFERENCES asset_heads(asset), job TEXT REFERENCES jobs(id), PRIMARY KEY(asset,job));
        CREATE TRIGGER IF NOT EXISTS serial_observations_no_update BEFORE UPDATE ON serial_observations BEGIN SELECT RAISE(ABORT,'Identity observations are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS serial_observations_no_delete BEFORE DELETE ON serial_observations BEGIN SELECT RAISE(ABORT,'Identity observations are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS asset_bindings_no_update BEFORE UPDATE ON asset_bindings BEGIN SELECT RAISE(ABORT,'Identity binds are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS asset_bindings_no_delete BEFORE DELETE ON asset_bindings BEGIN SELECT RAISE(ABORT,'Identity binds are immutable'); END;
        CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, at TEXT NOT NULL, event TEXT NOT NULL, data TEXT NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL);
        