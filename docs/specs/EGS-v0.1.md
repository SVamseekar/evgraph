# Evidence Graph Specification (EGS)

**Version:** 0.1 (Proposed)
**Status:** Draft — not an industry standard. This is a proposed specification for the `evgraph` open-source Python ecosystem. It is expected to change based on findings from the reference implementation.

---

## 1. Scope and Non-Goals

### 1.1 Scope

EGS defines the **Evidence Graph**: the canonical intermediate representation that all `evgraph` adapters produce and all `evgraph` rules consume. It specifies:

- The structural model (nodes, edges, graph)
- Identity and typing rules
- Mutability and lifecycle
- A minimal serialization format
- The minimal query operations rules are guaranteed to be able to perform

EGS exists to test one hypothesis: **that a single graph representation can serve as a faithful, sufficient intermediate form between heterogeneous AI-system artifacts and rule-based evaluation.** Every concept in this document is included because a concrete case in the `evgraph` reference implementation required it. Nothing is included on the basis of anticipated future need.

### 1.2 Non-Goals (v0.1)

The following are **explicitly out of scope for v0.1**. Each entry states why, so a future version can revisit it against real evidence rather than speculation.

| Deferred concept | Why deferred |
|---|---|
| **Cycles** | No reference use case (audit trails, lineage, approval chains) has required a cycle. Graphs are DAGs in v0.1. Revisit only if a real artifact demands a cyclic reference. |
| **Temporal/interval edges** | Timestamps exist on nodes (§3.2) but no edge-level temporal semantics (e.g., "valid from/to") are defined. No reference rule needed this yet. |
| **Evidence expiry / TTL** | Whether evidence can go stale is a rule-level concern (a rule can check a node's timestamp against a policy), not a graph-structural one. Revisit if expiry needs to affect graph traversal itself, not just rule logic. |
| **Node/edge mutability** | v0.1 graphs are immutable snapshots (§4). In-place mutation, patching, or merging of graphs is not defined. |
| **Graph versioning / diffing** | No mechanism for comparing two graph snapshots or representing "graph v2 supersedes graph v1" exists yet. Each `scan()` produces one immutable graph. |
| **Namespacing / multi-tenant identifiers** | Node IDs are scoped to a single graph (§3.1). Cross-graph or cross-organization identity resolution is not addressed. |
| **Subgraphs as first-class objects** | Traversal (§6) can produce a subset of nodes/edges, but that subset is not a typed, storable, independently-serializable object in v0.1. |
| **Query language** | v0.1 defines only the fixed traversal operations in §6 (`trace`, `neighbors`, `ancestors`, `descendants`). No general query DSL (Cypher-like or otherwise) is specified. |
| **Storage backend** | EGS defines an in-memory structural model and a serialization format (§5). It does not mandate or design any persistent store. |
| **Hypergraph / property-graph edge properties beyond a fixed set** | Edges carry a fixed, small property set (§3.3). Arbitrary user-defined edge properties are not supported in v0.1. |

If a future version of EGS adds any of the above, it must cite the specific reference-implementation case that required it, per §1.1.

---

## 2. Core Terminology

| Term | Definition |
|---|---|
| **Evidence Graph** | An immutable, directed acyclic graph produced by one or more adapters from one or more source artifacts. |
| **EvidenceNode** | A single observed fact or artifact reference within the graph (e.g., "this Model Card exists," "this approval record exists"). |
| **EvidenceEdge** | A directed, typed relationship between two nodes (e.g., `DERIVED_FROM`, `APPROVED_BY`). |
| **Adapter** | A component that converts an external artifact into nodes and edges. See APS-Core (companion spec) for the adapter contract; EGS defines only what an adapter *produces*, not how it produces it. |
| **Source Reference** | A pointer from a node back to the raw artifact/location it was derived from (file path, row range, API record ID, etc.), for traceability. |
| **Snapshot** | One complete, immutable Evidence Graph as returned by a single `scan()` (or equivalent) call. |

Terms not defined here (`Finding`, `Verdict`, `Rule`, `Requirement`) belong to RES and are out of scope for this document.

---

## 3. Graph Model

### 3.1 Node Identity

- Every `EvidenceNode` has an **`id`**: a string, unique within the containing graph.
- IDs are assigned by the adapter that creates the node. EGS does not mandate an ID scheme (UUID, content hash, sequential) — only that it be unique within the graph.
- IDs are **not** guaranteed stable across two different `scan()` runs over the same underlying artifacts unless a specific adapter documents that guarantee. (Cross-run identity stability is a candidate for a future EGS version, once a reference use case — e.g., diffing two scans — requires it. See §1.2.)

### 3.2 EvidenceNode Structure

```
EvidenceNode:
    id: str                     # unique within the graph
    type: str                   # e.g., "ModelCard", "HumanApproval", "DeploymentRecord"
    observed_at: datetime       # when the adapter observed this fact (not when the artifact was created)
    source: SourceReference     # where this node came from
    evidence_level: EvidenceLevel   # see §3.4 — set by the producing adapter
    attributes: dict[str, JSONValue]  # type-specific data, e.g. {"model_name": "..."}
```

- `type` is an open string, not a closed enum. Rule packs and adapters are expected to agree on type vocabularies out-of-band (this is what CVS, a separate future spec, is for). EGS does not enumerate valid node types — doing so would require EGS to anticipate every artifact type in advance, which contradicts §1.1.
- `attributes` is an open, JSON-compatible key-value map. EGS does not constrain its contents beyond requiring JSON-serializable values (§5).

### 3.3 EvidenceEdge Structure

```
EvidenceEdge:
    source_id: str       # id of the origin EvidenceNode
    target_id: str       # id of the destination EvidenceNode
    type: str             # e.g., "DERIVED_FROM", "APPROVED_BY", "SUPPORTS"
    observed_at: datetime
```

- Edges are directed. There is no undirected edge concept in v0.1.
- Like node `type`, edge `type` is an open string; EGS does not enumerate valid edge types.
- Edges carry no `attributes` map in v0.1 — only the four fields above. This is a deliberate minimality choice (§1.2); if a reference rule needs edge-level metadata beyond `type`, that is grounds for a v0.2 change, not a v0.1 workaround.

### 3.4 Evidence Level

Every node declares the epistemic status of how it was produced:

```
EvidenceLevel (enum):
    STRUCTURAL      # objective existence/absence of an artifact or field
    CONSISTENCY     # derived by cross-referencing two or more structural facts
    HEURISTIC       # produced by a probabilistic or pattern-based method
    INTERPRETIVE    # requires human-level judgment to have produced reliably
```

This is the same four-level hierarchy used by RES for `Finding.level`. It is defined here, not in RES, because it originates at the point evidence enters the graph — an adapter, not a rule, is what first claims "this fact is objective" or "this fact is a heuristic guess." RES findings inherit and may only *lower* confidence relative to the evidence levels of the nodes they cite, never claim a higher certainty than their source evidence.

### 3.5 Evidence Graph Structure

```
EvidenceGraph:
    graph_id: str                  # unique identifier for this snapshot
    created_at: datetime
    nodes: list[EvidenceNode]
    edges: list[EvidenceEdge]
    adapter_manifest: list[AdapterInvocation]   # which adapter(s) produced this graph, and their declared metadata (APS-Core)
```

- A graph MUST be acyclic (§1.2 — cycles are a non-goal).
- A graph MAY be disconnected (multiple components). Nothing in v0.1 requires a single connected graph — e.g., a `scan()` over an unrelated CSV and a Model Card may produce two disjoint components in one graph.
- `adapter_manifest` exists so that a consumer of the graph can determine, for any node, which adapter produced it and under what declared assumptions (this is the hook into APS-Core; full manifest schema is defined there, not here).

---

## 4. Mutability and Lifecycle

- An `EvidenceGraph`, once returned by an adapter or by `scan()`, is **immutable**. No operation in EGS v0.1 modifies an existing graph's nodes or edges in place.
- Combining evidence from multiple adapters is done by **graph union at construction time** (merging node/edge lists into one new graph before it is considered "complete"), not by mutating an existing graph after the fact.
- There is no defined mechanism for incremental/streaming graph construction in v0.1. A graph is either fully constructed or does not yet exist.

---

## 5. Serialization Format

- The canonical serialization of an `EvidenceGraph` is **JSON**, with the structure in §3.5 encoded directly (nodes and edges as arrays of objects, per §3.2/§3.3).
- `datetime` fields are serialized as ISO 8601 strings (UTC).
- `attributes` values must be JSON-serializable (string, number, boolean, null, array, or object). Adapters that need to reference non-JSON-serializable data (e.g., a DataFrame) must store a `SourceReference` pointer instead of embedding the object.
- No binary serialization format is defined in v0.1. If a reference use case demonstrates a performance need (e.g., very large graphs), a binary format (Arrow-backed, most likely, given the ecosystem's stated influences) is a candidate for a later version — not designed speculatively now.
- Schema versioning: every serialized graph MUST include an `egs_version` field at the top level (e.g., `"egs_version": "0.1"`) so consumers can detect incompatible future changes. No further compatibility guarantees are made in v0.1 (see §7).

---

## 6. Traversal Operations

EGS v0.1 guarantees that any conforming implementation supports exactly these operations. This is deliberately smaller than a general query language (§1.2):

| Operation | Signature | Behavior |
|---|---|---|
| `neighbors(node_id)` | → `list[EvidenceNode]` | Nodes directly connected to `node_id` by one edge, either direction. |
| `ancestors(node_id)` | → `list[EvidenceNode]` | All nodes reachable by following edges backward (target → source) transitively. |
| `descendants(node_id)` | → `list[EvidenceNode]` | All nodes reachable by following edges forward (source → target) transitively. |
| `trace(node_id)` | → `list[EvidenceEdge]` (ordered path) | The edge path connecting `node_id` back to its root ancestor(s); this is the operation `report.trace(...)` in the public API is built on. |

No other traversal primitive (shortest path, cycle detection beyond construction-time validation, pattern matching) is defined. Rule authors needing more than this in v0.1 operate on `nodes`/`edges` lists directly.

---

## 7. Compatibility and Versioning Rules

- EGS versions follow `MAJOR.MINOR`. v0.1 is pre-1.0: **no compatibility guarantees are made between 0.x versions.** This will change once EGS reaches 1.0.
- A breaking change to the structural model (§3) requires a MAJOR (or, pre-1.0, any) version bump and must be justified against §1.1's grounding rule — cite the reference-implementation case that required it.
- Adapters and rule packs SHOULD declare which EGS version they were built against (`egs_version`, §5) so tooling can detect mismatches. EGS v0.1 does not define automatic migration between versions.

---

## 8. Extension Points

EGS v0.1 defines exactly one extension point: **open `type` strings** on nodes and edges (§3.2, §3.3). This is intentional — it is the minimum extensibility needed for adapters and rule packs to introduce new vocabulary without changing this specification.

No plugin/hook mechanism is defined here. Adapter and rule extension mechanisms belong to APS-Core and RES respectively, not to EGS, which governs only the data shape those mechanisms produce and consume.

---

## 9. Conformance Requirements

An implementation conforms to EGS v0.1 if it:

1. Represents graphs as directed, acyclic structures of typed nodes and edges matching §3.2–§3.3.
2. Assigns every node a unique-within-graph `id` and a declared `evidence_level` (§3.1, §3.4).
3. Treats constructed graphs as immutable (§4).
4. Can serialize to and deserialize from the JSON format in §5, including the `egs_version` field.
5. Supports the four traversal operations in §6.
6. Does not claim support for any item listed as a non-goal in §1.2 under the name "EGS" (an implementation MAY offer such features as its own extension, but must not represent them as part of EGS v0.1 conformance).

---

## 10. Illustrative Example

Source artifacts: a Model Card (JSON file) and a human approval record (CSV row), for one model deployment.

```json
{
  "egs_version": "0.1",
  "graph_id": "scan_2026-07-28T00:00:00Z_a1b2c3",
  "created_at": "2026-07-28T00:00:00Z",
  "nodes": [
    {
      "id": "n1",
      "type": "ModelCard",
      "observed_at": "2026-07-28T00:00:00Z",
      "source": {"path": "model_card.json"},
      "evidence_level": "STRUCTURAL",
      "attributes": {"model_name": "risk-scorer-v3", "has_intended_use": true}
    },
    {
      "id": "n2",
      "type": "HumanApproval",
      "observed_at": "2026-07-28T00:00:00Z",
      "source": {"path": "approvals.csv", "row": 42},
      "evidence_level": "STRUCTURAL",
      "attributes": {"approver": "J. Smith", "approved_at": "2026-06-15T00:00:00Z"}
    },
    {
      "id": "n3",
      "type": "DeploymentRecord",
      "observed_at": "2026-07-28T00:00:00Z",
      "source": {"path": "deploy_log.json"},
      "evidence_level": "STRUCTURAL",
      "attributes": {"deployed_at": "2026-06-10T00:00:00Z"}
    }
  ],
  "edges": [
    {"source_id": "n3", "target_id": "n1", "type": "DEPLOYS", "observed_at": "2026-07-28T00:00:00Z"},
    {"source_id": "n3", "target_id": "n2", "type": "REQUIRES_APPROVAL", "observed_at": "2026-07-28T00:00:00Z"}
  ],
  "adapter_manifest": [
    {"adapter": "evgraph-adapter-modelcard", "version": "0.1.0"},
    {"adapter": "evgraph-adapter-csv", "version": "0.1.0"}
  ]
}
```

Note the case this example surfaces and that a RES-level rule would catch: `DeploymentRecord.attributes.deployed_at` (2026-06-10) precedes `HumanApproval.attributes.approved_at` (2026-06-15) — approval occurred *after* deployment. This is exactly the kind of `CONSISTENCY`-level finding described in RES: EGS's job is only to make both facts available as traceable nodes; RES's job is to notice the inconsistency between them.

---

## Appendix: Open Questions for v0.2

Tracked here, not resolved, per the grounding discipline in §1.1 — each requires a concrete reference-implementation case before being addressed:

- Should node `type` and edge `type` eventually be constrained by a registered vocabulary (feeding into CVS), or remain permanently open strings?
- Does cross-run node identity stability matter once a "compare two scans over time" use case exists?
- Does `SourceReference` need a standard shape, or should it stay adapter-defined `dict`?
- **Observation vs. Evidence** (cross-spec, must be settled before RES is finalized — not an EGS defect, but a shared-vocabulary decision RES cannot silently redefine): does an `EvidenceNode` represent a raw observation that only becomes "evidence" once a rule cites it in a `Finding`, or is everything an adapter places in the graph already "evidence" by definition? EGS currently takes the latter position implicitly (the graph *is* the Evidence Graph, full stop). If RES's design surfaces a real case where that conflation causes a problem — e.g., a rule needing to distinguish "this fact exists" from "this fact supports a conclusion" — resolve it there and reflect the outcome back into this document's terminology (§2), rather than letting the two specs drift to different definitions of the same word.
