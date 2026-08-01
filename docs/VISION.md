Evident — Vision
Status: Living strategic document.
Unlike ARCHITECTURE.md, this document is not constitutional. Unlike ROADMAP.md, it is not an execution plan. Unlike the specifications (EGS, RES, …), it is not normative.
This document exists to answer one question:
If Evident succeeds, what does it become, why does it matter, and what research and ecosystem directions become possible?
Ideas described here are hypotheses, not commitments.
Nothing moves from this document into the roadmap or a specification without first being justified through implementation experience and architectural review.
1. Why Evident Exists
Modern software engineering has transformed many disciplines from manual processes into executable systems.
Infrastructure became Infrastructure as Code.
Testing became Continuous Integration.
Deployment became Continuous Delivery.
Observability became executable telemetry.
AI governance, however, remains overwhelmingly document-centric.
Organizations write:
PDFs
Policies
Checklists
Audit documents
Compliance reports
Internal procedures
These artifacts describe governance but are rarely executable.
Evident explores a different idea.
Rather than asking software engineers to read governance documents, Evident asks:
Can governance evidence itself become computationally represented, evaluated, traced, and reported through software?
The project does not seek to replace human judgment.
It seeks to make governance evidence computationally understandable.
2. The Core Hypothesis
Evident is built around two hypotheses.
Hypothesis 1
Governance evidence originating from heterogeneous AI systems can be represented through a common intermediate representation.
This is the role of the Evidence Graph.
Whether the evidence originates from
model cards,
deployment systems,
inference logs,
approval workflows,
audit artifacts,
documentation,
it can ultimately be expressed as connected evidence rather than isolated files.
This hypothesis is validated—or rejected—through EGS.
Hypothesis 2
Deterministic rules operating on that graph can produce reproducible, explainable findings without claiming authority they do not possess.
Rules do not determine legal compliance.
Rules evaluate evidence.
Humans interpret findings.
This hypothesis is validated—or rejected—through RES.
3. From Documents to Executable Governance
Traditional governance often looks like this:
Policies

↓

Humans

↓

Documents

↓

Audit
Evident explores a different execution model.
Artifacts

↓

Adapters

↓

Evidence Graph

↓

Rules

↓

Findings

↓

Reports

↓

Humans
The human remains the decision maker.
Software performs the repetitive evidence processing.
4. Governance Engineering
One possible long-term outcome is the emergence of a discipline we currently refer to as Governance Engineering.
This is not a claim that such a discipline already exists.
It is a working hypothesis.
Comparable engineering disciplines emerged only after executable tooling became common.
Examples include:
DevOps
Platform Engineering
Data Engineering
Observability Engineering
MLOps
Governance Engineering, if it emerges, would focus on building systems that continuously collect, organize, evaluate, explain, and report governance evidence.
Whether the wider industry adopts that terminology is intentionally left open.
5. Evidence as an Intermediate Representation
Many successful infrastructure projects define an intermediate representation.
Examples include:
Domain	Intermediate Representation
Compilers	LLVM IR
Columnar Analytics	Apache Arrow
Distributed Tracing	OpenTelemetry Spans
APIs	OpenAPI
Evident explores whether governance evidence can similarly be represented by a common intermediate representation.
The Evidence Graph is an experiment in that direction.
If the hypothesis proves false, the architecture should evolve accordingly.
6. Relationship to Existing Standards
Evident is not intended to replace existing standards.
Instead, it aims to provide an executable runtime that can consume, organize, and evaluate evidence originating from those standards.
Potential relationships include:
W3C PROV (provenance representation)
OpenLineage (data lineage)
OpenTelemetry (operational telemetry)
CEN/CENELEC technical standards supporting the EU AI Act
ISO management system standards
NIST AI Risk Management Framework
These standards define concepts, terminology, or governance practices.
Evident explores how software can execute against evidence derived from them.
7. The Layered Ecosystem
The project intentionally separates stable foundations from rapidly evolving extensions.
Reality

↓

Adapters

↓

Evidence Graph

↓

Rules

↓

Findings

↓

Reporters

↓

Humans
Everything above the Evidence Graph should be replaceable.
Everything below the Rule interface should be implementation detail.
8. The Python Ecosystem
Python is the reference implementation.
It is not the product.
The long-term ecosystem consists of independent packages.
Examples include:
Core
evident-core
Public API
evident
Adapters
evident-adapter-pandas
evident-adapter-polars
evident-adapter-spark
evident-adapter-duckdb
evident-adapter-mlflow
Rule Packs
evident-rule-eu-ai-act
evident-rule-iso42001
evident-rule-gdpr
Reporters
evident-report-json
evident-report-markdown
evident-report-html
evident-report-sarif
Research
evident-context
evident-provenance
Each package should evolve independently wherever practical.
9. Independent Implementations
If the specifications prove sufficiently stable, nothing requires Evident to remain Python-only.
Possible future implementations include:
Rust
Go
Java
TypeScript
Long-term success is not measured by Python downloads alone.
It is measured by specification adoption.
The strongest possible validation would be an implementation written independently that conforms to the specifications without reusing the Python reference implementation.
10. Community Vision
The project should eventually become larger than its original author.
Success means:
independent maintainers,
external rule packs,
external adapters,
independent reporters,
academic research,
enterprise adoption,
community governance.
The Python code is intended to be the beginning of the ecosystem rather than its center.
11. Research Directions
Research intentionally remains separate from implementation.
Possible directions include:
Context Virtualization
Replacing sensitive enterprise context with virtual representations before AI processing and rehydrating results locally.
Research questions include:
trust boundaries,
identity,
security,
provenance,
privacy.
Evidence Provenance
Cryptographic integrity of evidence.
Possible directions include:
Merkle trees,
digital signatures,
verification,
tamper detection.
Governance Analytics
Potential work includes:
graph analytics,
dependency analysis,
governance metrics,
coverage visualization,
longitudinal governance trends.
Rule Authoring
Future possibilities include:
visual rule editors,
AI-assisted rule generation,
regulation-to-rule translation,
rule verification.
Distributed Evidence Graphs
Research questions include:
graph partitioning,
distributed evaluation,
graph serialization,
petabyte-scale evidence,
streaming governance evaluation.
12. Open Research Questions
The following questions remain intentionally unanswered.
Is the Evidence Graph the correct intermediate representation?
How should Evidence Graphs be serialized at very large scale?
How should distributed evaluation work?
Can governance evidence be exchanged between vendors?
How should provenance interact with evidence graphs?
Can regulations be partially translated into executable rule systems?
How should AI-generated rules be validated and governed?
How should cryptographic lineage be preserved for AI-assisted rule authoring?
Can context virtualization become reusable infrastructure beyond Evident?
None of these questions should influence the core architecture until supported by implementation evidence.
13. Conformance
Specifications are intended to become implementation-independent.
Long-term success requires conformance testing rather than implementation reuse.
Eventually, independent implementations should be able to validate themselves through shared conformance suites rather than by comparing source code.
The specification—not the Python implementation—should become the authoritative reference.
14. Products Built on Evident
Evident itself remains infrastructure.
Possible products built upon it include:
enterprise governance platforms,
CI/CD governance tooling,
audit systems,
assurance platforms,
consulting tools,
regulatory reporting systems.
These are intentionally outside the scope of the core project.
15. Anti-Goals
Evident should never become:
a legal decision engine,
a compliance certification authority,
a dashboard-first platform,
a workflow engine,
a generic AI orchestration framework,
an LLM wrapper,
a document management system.
These may integrate with Evident.
They should not become Evident.
16. Long-Term Success
Technical success:
stable specifications,
conformance suites,
multiple independent implementations.
Community success:
external maintainers,
independent rule packs,
independent adapters,
independent reporters.
Research success:
academic publications,
conference talks,
adoption in teaching and research.
Ecosystem success:
A third-party project states:
"Compatible with the Evident Specifications."
without using the reference Python implementation.
At that point, the specifications have become more valuable than the original implementation.
17. The Governing Principle
Every idea in this document must pass through the same progression before becoming part of Evident:
Vision
    ↓
Research
    ↓
Prototype
    ↓
Reference Implementation
    ↓
Specification
    ↓
Conformance
    ↓
Ecosystem Adoption
Ideas do not become architecture because they are interesting.
They become architecture because implementation repeatedly demonstrates that they belong there.
