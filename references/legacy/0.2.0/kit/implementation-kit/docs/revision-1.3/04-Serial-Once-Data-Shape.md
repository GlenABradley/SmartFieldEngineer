# Serial once — immutable identity binding

[FLOOR] Classification is FLOOR; implementation state is `specified_not_implemented`; the companion JSON Schema describes structure and does not implement authorization, database constraints or migrations.

[FLOOR] “Once” means one verified capture reused by reference, not a ban on correcting errors, replacing assets, or resolving a conflicting observation.

[FLOOR] Use `(home_id, asset_id, revision)` as the bind reference; serial is an observed attribute, not the global primary key and never sufficient to join customer records.

[FLOOR] Preserve raw serial text and evidence; trim surrounding whitespace for the normalized value, but do not change case or punctuation unless an approved vendor-specific rule is recorded.

[FLOOR] Capture lifecycle is observation → verification → immutable bind revision; OCR is a proposal until a named verifier accepts it against the underlying evidence.

[FLOOR] Each verified bind contains source digest, observation time, capture method, verifier and verification time; a hash establishes integrity, not physical authenticity.

[FLOOR] Corrections append a new revision with predecessor and reason, never overwrite a prior bind or rewrite an issued document.

[FLOOR] Device replacement receives a new asset ID and an explicit replacement relationship even when it occupies the same rack position.

[FLOOR] Store the active bind pointer separately and update it atomically with an expected revision; if the expected revision changed, expose a conflict instead of choosing the last writer.

[FLOOR] A record with a source job must reference a job in the same Home; field-level permissions and Home access apply before lookup, retrieval, generation or export.

[FLOOR] Uniqueness is required on `(home_id, asset_id, revision)` and `bind_id`; repeated manufacturer/serial observations trigger review within the Home rather than automatic asset merging.

[FLOOR] A renderer requests the authorized bind, emits its verified serial, and records the exact bind revision in the generated artifact; absent, conflicting, withdrawn or inaccessible binds return an explicit unresolved result with no guessed value.

[FLOOR] Historical issued artifacts retain their original serial and bind revision; corrections generate a new artifact and an explicit supersession record.

[FLOOR] The active pointer may be withheld during identity dispute, while historical revisions remain auditable under permission.

[FLOOR] Required future integration tests cover OCR transcription error, same serial across Homes, concurrent corrections, unauthorized recall, a replaced device, lost evidence, and historical issued-document consistency.
