# Evident: Open-Source Python Ecosystem for Executable AI Governance

**Architecture Blueprint v0.1**

> **Superseded.** This is the original pre-critique blueprint. Current principles live in `docs/ARCHITECTURE.md`; current status/roadmap in `README.md`. Kept here for project history — notably, the PASS/FAIL/Confidence explainability model on this page was replaced by the leveled evidence hierarchy (see `docs/ARCHITECTURE.md`, ADR-0003), and the nine-repository ecosystem plan was replaced by a single monorepo with packages split out later (ADR-0002).

---

# Mission

Evident is **not** a SaaS platform, compliance dashboard, or enterprise product.

It is an **open-source Python ecosystem** that enables developers to build, execute, trace, and automate governance for AI systems.

The long-term vision is similar to what NumPy did for numerical computing, Pandas did for tabular data, SQLAlchemy did for database abstraction, and OpenTelemetry did for observability.

Evident aims to become the foundational Python ecosystem for **Computational Governance** (also referred to as Governance Engineering)—making governance executable rather than static documentation.

The project should always remain:

* Python-first
* Open-source
* Library-centric
* Extensible
* Developer-first
* API-first

It is **not** intended to become a monolithic enterprise application.

---

# Philosophy

Traditional governance looks like this:

Regulations

↓

Policies

↓

Documents

↓

Manual Reviews

↓

PDF Reports

Evident changes this into:

Regulations

↓

Machine-readable Rules

↓

Evidence Collection

↓

Evidence Graph

↓

Rule Evaluation

↓

Explainable Verdict

↓

Traceability

↓

Reports

↓

Remediation

Everything becomes executable.

---

# Core Design Principle

Every artifact in an AI system should be transformable into one common internal representation.

That representation is called the **Evidence Graph**.

Examples of external artifacts:

* CSV files
* JSON
* JSONL
* Parquet
* DuckDB
* Pandas DataFrames
* Polars DataFrames
* Spark DataFrames
* Snowflake tables
* BigQuery tables
* MLflow runs
* LangSmith traces
* OpenTelemetry spans
* Prompt logs
* Model Cards
* Human review records
* Risk assessments
* Deployment metadata
* Evaluation datasets

All of these become:

Evidence Graph

The entire ecosystem is built around this abstraction.

Nothing evaluates raw data directly.

Everything evaluates the graph.

---

# Long-Term Vision

Become the governance equivalent of:

NumPy → ndarray

Pandas → DataFrame

PyTorch → Tensor

Arrow → Arrow Table

OpenTelemetry → Span

Evident → Evidence Graph

The Evidence Graph is the canonical representation of governance evidence.

---

# Design Goals

The ecosystem should satisfy the following principles.

## Developer First

A developer should obtain value within minutes.

Example:

```python
from evident import scan

report = scan("logs.parquet")

print(report.risk_score)
```

No configuration.

No YAML.

No policy writing.

No dashboards.

Immediate value.

---

## Explainability

Every decision must explain itself.

Not merely:

PASS

FAIL

Instead:

Requirement

Status

Confidence

Evidence Chain

Missing Evidence

Suggested Remediation

Trace

---

## Extensibility

Everything should be replaceable.

Adapters

Rules

Reporters

Context Providers

Evidence Stores

should all be plugins.

---

## Layered Architecture

Each layer depends only on lower layers.

High-level components must never leak into the core.

---

# Ecosystem Overview

The project is an ecosystem rather than a single package.

```
evident-org/

    evident-core

    evident

    evident-rules

    evident-adapters

    evident-context

    evident-provenance

    evident-reporting

    evident-cli

    evident-examples

    evident-docs
```

Each repository has exactly one responsibility.

---

# Package Descriptions

## 1. evident-core

The most important package.

Everything depends on it.

It must remain stable.

Contains only foundational abstractions.

### Responsibilities

EvidenceGraph

EvidenceNode

EvidenceEdge

Evidence

Finding

Requirement

Rule

Verdict

Trace

Adapter Protocol

Reporter Protocol

Plugin Interfaces

Rule Engine

No regulations.

No CLI.

No Spark.

No Context.

No Provenance.

No enterprise integrations.

Core is intentionally small.

---

## 2. evident

This is the package most users install.

```
pip install evident
```

Public API only.

Examples:

```python
from evident import scan

report = scan(...)

report.trace(...)

report.explain(...)

report.export(...)
```

It composes functionality from other packages.

---

## 3. evident-rules

Contains governance rule packs.

Examples:

EU AI Act

ISO 42001

NIST AI RMF

GDPR

HIPAA

SOC2

Custom Rules

Rules are data + executable logic.

They are independent from the graph implementation.

Community members should be able to publish:

evident-rule-finra

evident-rule-healthcare

evident-rule-uk-ai

etc.

without modifying core.

---

## 4. evident-adapters

Converts external systems into Evidence Graphs.

Possible adapters:

CSV

JSON

JSONL

DuckDB

Parquet

Arrow

Pandas

Polars

Spark

Snowflake

BigQuery

Databricks

MLflow

LangSmith

Weights & Biases

OpenTelemetry

Azure ML

Vertex AI

Each adapter implements the Adapter Protocol.

Rule Engine never changes.

Only adapters change.

---

## 5. evident-reporting

Responsible only for outputs.

Examples:

JSON

Markdown

HTML

PDF

SARIF

JUnit XML

GitHub Checks

GitLab Reports

No evaluation logic.

---

## 6. evident-context

Advanced package.

Purpose:

Context Virtualization.

Pipeline:

Real Context

↓

Virtual Objects

↓

LLM

↓

Response

↓

Rehydration

↓

Evidence Graph

This is **not** simple PII masking.

The LLM operates on virtualized objects rather than raw sensitive data.

The Evidence Graph records virtual references.

Rehydration occurs locally.

---

## 7. evident-provenance

Responsible for integrity.

Possible features:

Hash chains

Merkle Trees

Cryptographic Anchoring

Digital Signatures

Verification

Tamper Detection

No governance logic.

No adapters.

Only provenance.

---

## 8. evident-cli

Thin wrapper around Python API.

Commands:

scan

report

trace

doctor

rules

graph

validate

Should contain almost no business logic.

---

# Core Object Model

Everything revolves around a small number of objects.

Evidence

Represents observed facts.

Finding

Represents detected governance issues.

Requirement

Represents one governance obligation.

Rule

Executable logic that evaluates evidence.

Verdict

Result produced by rule evaluation.

Trace

Lineage explaining how a verdict was reached.

EvidenceNode

Node within the graph.

EvidenceEdge

Relationship between nodes.

EvidenceGraph

Canonical graph representation.

Adapter

Converts external artifacts into graph objects.

Reporter

Converts findings into human-readable outputs.

Plugin

Extension mechanism.

---

# Evidence Graph

The graph is the heart of the ecosystem.

Every adapter outputs a graph.

Every rule consumes the graph.

Every report originates from the graph.

Example lineage:

Decision

↓

Model

↓

Training Dataset

↓

Risk Assessment

↓

Human Approval

↓

Deployment

↓

Inference

↓

Audit Anchor

Graph traversal powers:

trace()

explain()

lineage()

impact analysis

dependency analysis

---

# Rule Engine

Rules consume graph objects.

Rules emit findings.

Findings become verdicts.

Verdicts become reports.

Rules should support:

confidence

severity

evidence chain

missing evidence

remediation

---

# Explainability

Every verdict must answer:

What failed?

Why?

What evidence supported this?

What evidence was missing?

How confident is the result?

How can it be fixed?

Example:

Requirement

EU AI Act Article 13

Status

PASS

Confidence

0.94

Evidence

Model Card

Human Approval

Deployment Record

Missing

None

Remediation

Not Required

---

# Python API

The API should feel extremely simple.

```python
from evident import scan

report = scan("logs.parquet")

report.summary()

report.findings()

report.trace("decision_843")

report.export("html")

report.export("json")
```

---

# CLI Experience

```
evident scan logs.parquet
```

Output:

Risk Score

Findings

Missing Evidence

Suggested Fixes

If optional packages could help:

Install:

pip install evident[context]

or

pip install evident[provenance]

---

# Progressive Ecosystem

Day 1

pip install evident

Day 30

Install rule packs

Day 90

Install provenance

Day 180

Install context virtualization

Day 365

Build custom plugins

The ecosystem grows naturally.

---

# Extension Model

External developers should implement protocols rather than modifying source code.

Examples:

Custom Adapter

Custom Rule

Custom Reporter

Custom Context Provider

Custom Evidence Store

The ecosystem should encourage independent packages.

---

# Dependency Direction

Dependencies must always flow downward.

```
evident-cli
      │
      ▼
evident
      │
 ┌────┼────┐
 ▼    ▼    ▼
rules adapters reporting
      │
      ▼
context provenance
      │
      ▼
evident-core
```

Core depends on nothing else.

Everything depends on Core.

Never create circular dependencies.

---

# Documentation Strategy

Structure documentation similarly to mature Python ecosystems.

Getting Started

15-Minute Guide

Core Concepts

Evidence Graph

Rule Engine

Adapters

Reporting

Tracing

Plugin Development

Architecture

API Reference

Contribution Guide

---

# What Is Explicitly Out of Scope for Initial Versions

The first releases should not attempt to become:

* A hosted SaaS
* A compliance dashboard
* A Kubernetes admission controller
* A workflow orchestrator
* A replacement for MLflow
* A replacement for OpenTelemetry
* A legal interpretation engine
* A document management system

Instead, Evident should integrate with these systems where appropriate.

---

# Long-Term Goal

The long-term ambition is not to "build another governance library."

The ambition is to establish a common execution model for governance evidence in Python.

Just as many projects exchange Arrow Tables or OpenTelemetry spans, the ecosystem should eventually enable tools to exchange governance information through a stable, extensible Evidence Graph abstraction.

Success is measured not only by adoption of the main package, but by the emergence of independent adapters, rule packs, reporters, and integrations built by the community on top of the core interfaces.
