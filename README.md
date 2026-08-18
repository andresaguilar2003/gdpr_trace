# GDPR Trace Compliance Framework

This repository contains a model-driven and LLM-assisted framework for GDPR-aware enrichment and validation of process-mining event logs. The system transforms raw event logs into enriched traces and graphs, adds GDPR-relevant context and compliance evidence, and validates the resulting artefacts using deterministic rule-based checks and OCL specifications.

The project combines process mining, model-driven engineering, large language models, mutation-based evaluation, and OCL-based compliance validation. It has been developed around healthcare and financial event-log scenarios, with special attention to GDPR concepts such as legal basis, purpose limitation, health-data processing, consent, retention, third-party transfers, and data-subject rights.

## Repository Structure

### `/app`

Source code of the main application. It includes the UI, controllers, services, models, enrichment pipeline, mutation engine, AI-assisted components, and deterministic GDPR validation logic.

### `/OCL_rules`

Standalone catalogue and documentation of the OCL rules used for GDPR compliance validation. The main catalogue is available in `OCL_Rules_Catalog.md`.

### `/docs`

General project documentation, supporting material, and paper-related documentation.

### `/experiments`

Experimental scripts and results for the three main studies:

- T5-small based GDPR validation.
- RoBERTa vs Phi-3 comparison for context inference and activity typing.
- OCL rule auditing, optimisation, and consolidation.

### `/data`

Input and output event logs used by the system. The `input` folder contains source logs to be processed, while the `output` folder stores enriched or generated logs.

## Main Goal

The goal of the project is to support reproducible GDPR compliance analysis over event logs by making regulatory context explicit, enriching traces with compliance evidence, and validating the result through formal and deterministic rules.
