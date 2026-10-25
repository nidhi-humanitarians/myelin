# Myelin: Semantic JIT Compiler for AI Agents
> Compiling repetitive agent decision streams into fast, model-free, deterministic Python code with calibrated abstention.

---

## 1. What is Myelin?

In human neurobiology, **myelination** is the process where repetitive electrical signaling wraps active neural pathways in a protective sheath, allowing signals to travel up to 100x faster without conscious mental effort.

**Myelin** applies this exact mechanism to autonomous AI agents:
1. **Monitors Trace Streams:** Ingests execution logs (such as `tau-bench` customer service or `SWE-agent` coding sessions).
2. **Spots Habits:** Discovers recurring decision points (clusters of $\ge 50$ identical micro-tasks).
3. **Compiles to Deterministic Code:** Uses a frontier LLM to synthesize pure Python functions using regex, BM25 lexical routing, and boolean decision masks.
4. **Enforces Calibrated Abstention:** Every compiled function executes under a strict contractâ€”it solves routine cases in sub-millisecond local execution, but returns an explicit `"unsure"` when inputs are ambiguous or drift.
5. **Enforces a $\ge 98\%$ Agreement Gate:** In a zero-network, zero-model sandbox on held-out future sessions, the compiled code must achieve $\ge 98\%$ accuracy on all non-abstained decisions.

---

## 2. Directory Structure

```text
myelin/
â”œâ”€â”€ README.md                      # Project overview, philosophy, and quickstart
â”œâ”€â”€ docs/
â”‚   â””â”€â”€ DESIGN_SPECIFICATION.md    # Complete technical design doc & architecture
â”œâ”€â”€ insights/
â”‚   â””â”€â”€ EMPIRICAL_FINDINGS.md      # Analysis of tau-bench traces and bottleneck discoveries
â””â”€â”€ data/
    â””â”€â”€ historical_trajectories/   # Real agent execution trajectories (GPT-4o & Sonnet 3.5)
```

---

## 3. Core Architectural Principles

* **When Cheap $\rightarrow$ Pick Specialization:** Compiled Python primitives (regex, BM25, bit-masks) run in microseconds at $0.00 cost on ordinary CPUs.
* **When Expensive $\rightarrow$ Pick Generalization:** The multi-billion parameter frontier model is called only when specialized code returns `"unsure"`.
* **Zero Catastrophic Forgetting:** Each compiled habit is an independent, versioned Python micro-tool. Adding 100 new habits will never degrade existing ones.

---

## 4. Documentation & References

* See `docs/DESIGN_SPECIFICATION.md` for full implementation roadmaps, baseline setups, and pipeline diagrams.
* See `insights/EMPIRICAL_FINDINGS.md` for concrete frequency breakdowns and the Reservation Traversal Loop case study.
