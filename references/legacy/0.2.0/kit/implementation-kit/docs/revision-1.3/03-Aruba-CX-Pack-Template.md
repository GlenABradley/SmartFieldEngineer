# Platform Pack template — Aruba CX access-port change

[HORIZON] Pack ID `aruba-cx.access-port.v0.1`; state `template_not_released`; reference family `AOS-CX 10.15, 6000/6100`; tested model/firmware list is empty.

[FLOOR] This is a reviewable template, not executable configuration or a released device driver; exact SKU and firmware must be bound and qualified before use.

[HORIZON] Purpose: give an engineer with Cisco experience the semantic questions, evidence and recovery discipline needed to change one approved endpoint port on a supported CX switch.

[FLOOR] ArubaOS-Switch, other CX series, and Hirschmann products require separate model/firmware bindings; brand similarity or familiar command text is not compatibility evidence.

## Required input contract

| Label | Input | Constraint |
|---|---|---|
| FLOOR | Identity | Home, job, asset bind/revision, exact SKU, firmware build, serial provenance |
| FLOOR | Intent | Endpoint purpose, target interface, required untagged/tagged behavior, VLAN identity and expected reachability |
| FLOOR | Existing reality | Current interface role, VLAN membership, authentication, aggregation, topology, management dependency and configuration owner |
| FLOOR | Authority | Scope revision, permitted actor, approved outage, exact reviewed plan hash and rollback authority |
| FLOOR | Recovery | Verified console or other independent recovery path, configuration baseline, responsible recovery operator |
| FLOOR | Evidence | Raw before/after outputs and checks, endpoint observations, capture time, parser version and source digest |

## Cisco experience → semantic checkpoints

| Label | Familiar intent | Question the pack must settle before choosing syntax |
|---|---|---|
| HORIZON | Access port | Which frames should be admitted untagged, which VLAN receives them, and is this really an endpoint rather than an uplink? |
| HORIZON | Trunk/native VLAN | What tagging is expected on each end, which VLANs are admitted, and could a native/untagged mismatch expose the wrong network? |
| HORIZON | EtherChannel | Is the interface part of an aggregation, and what negotiated/static behavior and peer assumptions apply? |
| HORIZON | SVI / default route | Which management or routed context is intended, and does the exact model support the required behavior? |
| HORIZON | Save configuration | Which state is running, which persists after restart, and what evidence proves both states reflect the approved result? |
| HORIZON | Rollback | Which pre-change state is recoverable, what intervening changes would be overwritten, and how is access retained? |

## Bounded procedure

[HORIZON] Step 1 — identify and bind the actual device and firmware; compare against the released compatibility matrix and stop if unmatched.

[HORIZON] Step 2 — collect before-state and determine whether local CLI changes are appropriate under the site's configuration-management ownership; stop on ambiguity, uplink/aggregation membership, management-path dependency, or unscoped authentication behavior.

[HORIZON] Step 3 — construct a semantic diff for one endpoint port, preserve unrelated settings, explain expected service impact, and resolve missing VLAN or endpoint requirements before rendering commands.

[HORIZON] Step 4 — have the qualified reviewer bind the rendered model-specific plan and recovery plan to an Approval Aperture; any change to device, pack, intent or before-state invalidates the reviewed plan.

[HORIZON] Step 5 — verify recovery access, capture the recoverable baseline, apply only the approved diff through a qualified operator, and retain actual responses rather than inferred success.

[HORIZON] Step 6 — confirm port state and intended VLAN behavior, endpoint addressing and agreed service reachability, plus absence of unintended access to a denied test destination; compare raw observations against agreed pass criteria.

[HORIZON] Step 7 — only after verified acceptance, make persistence an explicit approved action and record the resulting persistent state; otherwise use the approved recovery procedure and verify restored service.

[FLOOR] A failed or timed-out change is an unknown state until inspected; do not blindly replay or roll back across another operator's intervening work.

## Source binding and release gates

[FLOOR] HPE documents checkpoints and copying running configuration to startup configuration or a checkpoint for this reference family; inspect the precise command context, syntax and effects in the [AOS-CX 10.15 CLI guide for 6000/6100](https://arubanetworking.hpe.com/techdocs/AOS-CX/10.15/PDF/cli_6000-6100.pdf), checkpoint commands section, before producing a device-specific executable plan.

[FLOOR] The reference guide is a compatibility starting point, not evidence that a particular switch or firmware was tested here.

[HORIZON] Release requires a populated exact-SKU/firmware matrix and observed tests for allowed endpoint traffic, denied VLAN traffic, loss of management, wrong interface, missing VLAN, authentication conflict, interrupted session, persistence, recovery, and concurrent configuration drift.

[HORIZON] The released pack must retain source-document hashes/revisions, reviewer identity, test fixtures and actual outputs, known limitations, and a deprecation path when firmware behavior changes.
