# AI–Human Provenance Standard

## Disclosure

This repository contains substantial AI-assisted engineering work. The original project direction and repository were supplied by the human owner; the production-hardening pass, code changes, tests, configuration, and documentation were generated with AI assistance under explicit human direction.

Do **not** describe this repository as unaided human authorship. Use evidence to distinguish what the human can personally implement, explain, modify, debug, and defend from what AI produced.

## Attribution labels

| Label | Meaning |
|---|---|
| Human-authored | Written independently by the human and preserved as such. |
| Human-directed / AI-assisted | Human selected the problem, constraints, and acceptance criteria; AI proposed or implemented changes. |
| AI-generated / human-verified | AI produced the artifact; the human later ran, reviewed, modified, and accepted it. |
| AI-generated / pending human verification | AI produced it, but live execution or ownership proof is still outstanding. |
| External/generated | Produced by a framework, provider, dependency, or generated build process. |

## Current release provenance

| Surface | Provenance | Claim allowed now |
|---|---|---|
| Original product concept and prioritization | Human-directed | The human selected and shaped the problem. |
| Production-hardening changes | AI-generated / pending human verification | The repository contains these changes; unaided implementation must not be claimed. |
| Offline tests run in this upgrade environment | AI-executed and recorded | The listed commands passed in the upgrade environment. |
| Live deployment, provider credentials, user validation, benchmarks, dashboards, and chaos demos | Pending human verification | No claim until the human executes and preserves evidence. |
| Future BRAAT reconstruction/debugging sprints | Human execution with AI evaluation | May become human competence evidence after successful completion. |

## Human ownership gate

Before presenting a subsystem as personal competence, the human must be able to:

1. explain its responsibility, inputs, outputs, invariants, state, and failure modes without notes;
2. reconstruct or materially modify a signal-bearing part;
3. diagnose a realistic failure using evidence rather than random edits;
4. run the relevant tests and deployment commands;
5. defend the major design tradeoffs;
6. identify which portions were AI-assisted.

## Recommended public disclosure

> This project was developed with substantial AI assistance. I directed the problem framing and acceptance criteria, then validated the implementation through repository inspection, tests, reconstruction exercises, debugging sprints, and live deployment checks. The evidence index distinguishes AI-generated artifacts from the parts I can independently implement and defend.

## Prohibited claims

- “I wrote every line myself.”
- “Production-proven” without a real production run.
- “Scalable,” “resilient,” or “low latency” without measurements.
- “Human-authored” for AI-generated code merely reviewed visually.
- Invented users, metrics, incidents, benchmarks, or deployment results.
