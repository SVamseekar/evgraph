# Practitioner Outreach Kit — Stage 4.5 Goal 3

**Status:** Runnable preparation for H3 (`docs/research/validation-plan.md`). Not a marketing plan. Interviews are the work; this kit only makes them repeatable.

**Prior context:** Desk research in `docs/research/practitioner-and-market-check.md` leans negative (fragmented ownership; banking MRM already served; common failure is “docs never written,” not “wrong format”). Goal 3 tests whether *direct* conversations contradict, refine, or confirm that picture. Do not pitch adoption; listen for a recurring problem.

---

## 1. One-page explanation (say this, then stop)

### What Evgraph is

Evgraph is a small open-source **Python library stack** (not a SaaS product). It:

1. Reads artifacts you already have (Model Cards, approvals, deployment records, dataset manifests, MLflow registry metadata).
2. Builds an **Evidence Graph** — a shared, typed intermediate representation.
3. Runs **deterministic rules** that emit **leveled, citeable findings** (what evidence exists, is missing, or is inconsistent).
4. Exports the same findings as Markdown, SARIF, JSON, or OSCAL Assessment Results — including an optional **CI promotion gate** (`evgraph scan-promotion`, report-only by default; `--gate` / `--strict` when you want a non-zero exit).

Install: `pip install evgraph evgraph-cli` (optional: `evgraph[mlflow]`). Current release train: **0.1.2** on PyPI.

### What Evgraph is not

- Not a compliance certificate, legal opinion, or PASS/FAIL severity product.
- Not a dashboard, workflow orchestrator, or document management system.
- Not a replacement for MLflow / registries / your source of truth — adapters read them; Evgraph does not own them.
- Not an LLM wrapper; default evaluation is deterministic.

Full boundary list: `docs/ARCHITECTURE.md` §5. Findings use evidence outcomes (`EXPECTATION_MET` / `EXPECTATION_NOT_MET` / `INCONCLUSIVE`), never bare compliance verdicts (ADR-0003).

### Why we are talking to you

We already validated the architecture internally and against OSCAL + MLflow (`docs/research/oscal-roundtrip.md`, `docs/research/mlflow-adapter-validation.md`). We have **not** validated that this solves a real day-to-day problem for people who own AI governance evidence. That is the only question this conversation is for.

---

## 2. Demo script (5–10 minutes)

**Setup (before the call):** from a clone with packages installed (or `pip install evgraph evgraph-cli`), repo root as cwd.

| Minute | Do / say |
| --- | --- |
| 0–1 | One-page explanation above. Emphasize *evidence findings*, not compliance. |
| 1–4 | Run the promotion scan on the shipped sample trio (known inconsistent case from the Stage 1 worked example): |

```bash
evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format markdown
```

Point at: rule id, outcome, evidence level, citations back to nodes — **why**, not a green/red badge.

| Minute | Do / say |
| --- | --- |
| 4–6 | Same inputs, CI-shaped output (and mention gate is opt-in): |

```bash
evgraph scan-promotion \
  --model-card examples/model_card_deployment/model_card.json \
  --approval examples/model_card_deployment/approval.json \
  --deployment examples/model_card_deployment/deployment.json \
  --format sarif
# Optional: add --gate (exit 1 on EXPECTATION_NOT_MET) or --gate --strict
```

If useful: “Same findings → Markdown for reviewers, SARIF for CI, OSCAL for standards tools” — show one line of OSCAL or open `examples/promotion_gate/README.md` rather than lecturing.

| Minute | Do / say |
| --- | --- |
| 6–8 | Stop demoing. Ask the **primary question** (below). Stay quiet after asking. |
| 8–10 | At most the optional follow-ups. Log answers in their words (`practitioner-interview-log.md`). |

**Do not:** invent a customer story, claim adopters, map their answer to a regulation as “compliant,” or extend into Stage 5 features.

**Optional alternate path (if they live in MLflow):** mention `evgraph[mlflow]` + promotion scan with registry + JSON trio exists; only demo it if you have a local registry ready. Prefer the JSON trio for reliability on a first call.

---

## 3. Interview questions

### Primary (required — ask exactly once, verbatim)

> What problem, if any, would this solve for you?

Accept “none,” “not our problem,” or “different problem” as success for the *method*. Success for *H3* requires a recurring pattern across independent people — see the decision memo.

### Optional follow-ups (pick at most 2–4; skip if the primary answer already covered them)

1. When promotion or release review happens in your org, **what evidence is missing or inconsistent most often** — and who notices?
2. Would a **CI gate** over evidence findings (report-only vs fail-on-unmet) help, hurt, or be irrelevant where you work?
3. Would a **reviewer pack** (same findings as Markdown + SARIF + OSCAL) change anything for model risk / governance review, or do you already have that trail another way?
4. Is the hard part **producing artifacts at all**, **stitching artifacts across systems**, **enforcing a check in CI**, or something else?

Do not ask “would you adopt Evgraph?” or “how much would you pay?” in this round — those are not H3.

---

## 4. Targeting

### Talk to (roles that own the workflow)

| Role | Why |
| --- | --- |
| ML platform / MLOps engineers | Own CI, registries, promotion pipelines; closest to the shipped promotion gate. |
| Model risk / MRM (esp. outside “already bought ValidMind-class suite”) | Own evidence packs and review; will say quickly if this is redundant. |
| AI governance / Responsible AI leads who ship process with engineering | Own cross-artifact review without necessarily owning a compliance product. |
| Staff/principal ML engineers who run release reviews in mid-size orgs | Often the informal owners when there is no dedicated MRM tool. |

Prefer people who can describe **last quarter’s** promotion/review pain in concrete terms.

### Where / how to find them (practical)

1. **Warm intros** — former coworkers, conference contacts, advisors who sit in platform or risk. Highest signal; start here.
2. **Title-targeted LinkedIn** — search “ML platform,” “MLOps,” “Model Risk,” “AI Governance” + your industry; short message (template below). Cap volume; quality over blast.
3. **Practitioner forums with role filters** — MLOps Community Slack; local MLOps / data-platform meetups; conf hallway (MLOps-focused events), not keynote crowds.
4. **Issue/discussion authors** on registry/CI topics (MLflow, Kubeflow, internal platform docs) who describe promotion evidence gaps — reply once, offer a 15-minute demo, no pitch deck.

### Who to avoid (for Goal 3)

- General AI hobby audiences, “AI news” Twitter/X, Show HN as the *validation* sample.
- People whose only frame is “AI ethics discourse” with no ownership of artifacts, CI, or review.
- Vendors pitching competing platforms (fine later for competitive intel; not H3 interviews).
- Anyone you would pressure into praise (friends who will say “looks cool” without a owned problem).

### Outreach message (copy/adapt)

> I’m validating an open-source library that turns Model Cards / approvals / deployment (and optionally MLflow) into citeable evidence findings for CI and reviewers — explicitly not a compliance product. 10-minute demo + one question: whether this solves any problem you actually have. Happy to hear “no.” Are you free for a short call?

---

## 5. Success metric (reminder)

| Counts | Does not count |
| --- | --- |
| Same **problem pattern** in their words across independent conversations | Stars, likes, “interesting,” “looks cool” |
| Clear map (or non-map) to what Evgraph already does | Promises to try it “someday” |
| Explicit “this is already solved by X” or “our problem is Y upstream” | Your own excitement after a good demo |

Log every conversation with `docs/research/practitioner-interview-log.md`. Decide with `docs/research/practitioner-decision-memo.md`.
