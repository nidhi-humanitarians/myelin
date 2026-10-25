# Technical Design Specification: Agent Habit Compiler
**Project ID:** 140 — Compile Your Own Habits  
**Domain:** Autonomous Agent Optimization & Compiled Agency  
**Target Benchmarks:** `tau-bench` (Customer Service / Airline & Retail), `SWE-agent`  
**Date:** October 2026  
**Status:** Approved for Implementation  

---

## 1. Executive Summary

Modern AI agents repeatedly invoke multi-billion parameter foundation models to perform trivial, deterministic micro-decisions—such as parsing user IDs, iterating over reservation lists, normalizing dates, and evaluating boolean policy rules. This creates substantial inference cost, unnecessary latency (1–2 seconds per call), and vulnerability to non-deterministic formatting failures.

The **Agent Habit Compiler** is an offline optimization pipeline that mines an agent's historical execution traces, clusters high-frequency decisions ($\ge 50$ occurrences), and synthesizes standalone, zero-cost, model-free Python functions to replace them. Each function operates under an **explicit abstention contract (`return "unsure"`)**: routine cases are executed in sub-millisecond local Python, while ambiguous or drifting edge cases safely fall back to the frontier model.

### Key Acceptance Criterion
* **Strict $\ge 98\%$ Agreement Gate:** Evaluated in a zero-network, zero-model sandbox on a held-out future test set (latest 30% by time), any compiled function must match verified model decisions on at least 98% of cases where it does not abstain.

---

## 2. Empirical Findings from `tau-bench` Traces

Analysis of real `tau-bench` trajectories (`gpt-4o-airline.json`, `sonnet-35-new-airline.json`, and `gpt-4o-retail.json`) revealed that agent workloads are heavily dominated by repetitive micro-tasks:

| Tool Call / Decision | Observed Occurrences | Dominant Pattern | Token & Latency Waste |
| :--- | :--- | :--- | :--- |
| **`get_reservation_details`** | **1,419+ calls** | Extracting 6-character alphanumeric PNRs or looping over user reservations | ~3,500 tokens & 1.5s per reservation lookup |
| **`get_order_details` (Retail)** | **1,029 calls** | Extracting numeric order IDs (`\d{7,10}`) | ~2,800 tokens & 1.4s per lookup |
| **`get_user_details`** | **875+ calls** | Extracting formatted usernames (`[a-z]+_[a-z]+_\d{4}`) | ~2,200 tokens & 1.3s per user extraction |
| **`search_direct_flight`** | **538+ calls** | Extracting origin/destination airport codes and dates | ~4,000 tokens & 1.8s per flight search |
| **`calculate`** | **96+ calls** | Basic arithmetic (baggage fees, ticket differences) | ~2,000 tokens & 1.2s for basic math |

### Case Study: The "Reservation Traversal Loop" Bottleneck
In Episode 2 of the airline benchmark, an agent looked up user `omar_davis_3817`. The profile returned 6 reservations: `['JG7FMM', 'LQ940Q', '2FBBAH', 'X7BYG1', 'EQ1G6C', 'BOH180']`.

* **Current Agent Behavior:** The LLM was queried **6 consecutive times in a row**, sending ~2,500 tokens of context each turn, just to emit the next reservation ID in the list.
* **Cost:** 15,000 tokens and ~9 seconds of user wait time.
* **Compiled Habit Alternative:** A 3-line Python list comprehension runs the exact same iteration in **0.002 milliseconds** at **$0.00** cost.

---

## 3. System Architecture & End-to-End Pipeline

```
                                  RAW TRACE LOGS
                   (tau-bench historical_trajectories / Pi harness)
                                         │
                                         ▼
                               [ 1. Trace Miner ]
                     Slices conversations into atomic records:
                     (input_context, model_output, timestamp)
                                         │
                                         ▼
                            [ 2. Job Clusterer & Splitter ]
                     • Groups by prompt template & input embeddings
                     • Filters for clusters with count >= 50
                     • Chronological Split: 70% Past (Train) / 30% Future (Test)
                                         │
                                         ▼
                            [ 3. Program Synthesizer ]
                     • Frontier LLM generates function.py + test_cases.py
                     • Enforces 'unsure' abstention contract
                     • AST validation (bans network, disk I/O, dangerous modules)
                                         │
                                         ▼
                            [ 4. Sandboxed Evaluator ]
                     • Runs function.py against 30% held-out test set
                     • Zero-network, zero-model sandbox
                     • Evaluates: Agreement Rate (>= 98% ?), Coverage %, Tokens Saved
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 PASS (>= 98% Acc)                FAIL (< 98% Acc)
                         │                               │
                         ▼                               ▼
                 [ 5. Habit Registry ]            [ Rejection Log ]
                 • Registers to Interceptor       • Feeds back failing cases
                 • Generates Agent Tool (.py)     • Refines prompt/guardrails
```

---

## 4. The Specialization vs. Generalization Philosophy

As established in compound systems design:
* **When Cheap $\rightarrow$ Pick Specialization:** Compiled Python functions utilize hyper-specialized, deterministic primitives (Regex, BM25 lexical scoring, Bit-mapping boolean tables). They execute in nanoseconds on standard CPUs without GPU dependencies.
* **When Expensive $\rightarrow$ Pick Generalization:** The frontier LLM is invoked only when the specialized code returns `"unsure"` or encounters out-of-distribution inputs.

### Algorithmic Building Blocks for Compiled Habits
1. **Regular Expressions (`re`):** For syntactic entity extraction (PNRs, user IDs, dates, order numbers).
2. **BM25 / Keyword Indexing:** For lexical routing to tools/departments without neural embedding overhead.
3. **Bit-Mapping & Decision Masks:** For evaluating multi-condition business rules (e.g., `is_basic_economy & within_24h_window`).
4. **Functional Composition:** Combining extraction and rules into a single deterministic execution block.

---

## 5. The Abstention Contract & Calibration (RLCD)

To satisfy the non-negotiable $\ge 98\%$ accuracy requirement, the system enforces a strict contract:
$$\text{Agreement Rate} = \frac{\text{Correct Predictions}}{\text{Total Predictions} - \text{Unsure Count}} \ge 0.98$$

### Why Calibration Matters
When evaluating machine learning baselines against compiled code:
* Standard models (trained via RLVR or uncalibrated fine-tuning) suffer from **overconfidence**—guessing aggressively on edge cases and failing the 98% threshold.
* **RLCD (Reinforcement Learning for Calibrated Decisions)** trains models using proper scoring rules (Brier loss) so that output confidence matches true empirical probability.
* In the compiled Python function, calibration is achieved structurally: any input failing strict regex/format bounds immediately returns `"unsure"`.

---

## 6. Baselines & Benchmark Comparison

Every compiled habit must be benchmarked against three mandatory baselines on the exact same 30% held-out test split:

1. **Baseline A (Semantic Cache):** Nearest-neighbor vector lookup on input embeddings (FAISS). Evaluates whether static lookup handles slight phrasing variance.
2. **Baseline B (Small Calibrated Classifier):** Logistic Regression / XGBoost or RLCD-calibrated classifier trained on the 70% split.
3. **Baseline C (Small Local LLM):** A 1B–3B parameter model (e.g., Qwen-2.5-1.5B or Llama-3.2-1B) with few-shot examples.

---

## 7. Deliverables & Repository Layout

The project will be delivered as a modular Python package (`habit-compiler`):

```text
habit-compiler/
├── pyproject.toml                     # Dependencies & CLI entry points
├── configs/
│   ├── default.yaml                   # 98% gate, >=50 cluster threshold, 70/30 split
│   └── tau_bench_adapter.yaml         # Field mappings for tau-bench trajectories
├── data/
│   ├── raw_traces/                    # Cloned tau-bench historical trajectories
│   └── processed/                     # Extracted decision records & splits
├── compiled_habits/                   # Output registry of verified habits
│   ├── extract_user_id/
│   └── extract_pnr/
├── src/habit_compiler/
│   ├── mining/                        # Trajectory parsing & decision slicing
│   ├── clustering/                    # Template identification & DBSCAN grouping
│   ├── synthesis/                     # Frontier LLM code generation & AST sanitizer
│   ├── sandbox/                       # Isolated evaluation runner (98% check)
│   ├── baselines/                     # Semantic cache, classifier, local LLM
│   ├── runtime/                       # Fast-path interceptor middleware
│   └── visualizer/                    # Monthly timeline dashboard generator
└── visual/
    └── dashboard.html                 # Interactive map of compiled habits
```

---

## 8. Implementation Roadmap (1-Week Sprint)

* **Phase 1 (Days 1–2): Ingestion & Slicing**
  * Implement `decision_slicer.py` targeting `tau-bench` airline/retail logs.
  * Extract atomic decision pairs into unified JSONL schemas.
* **Phase 2 (Day 3): Clustering & Temporal Splitting**
  * Build template extractor and embedder.
  * Cluster decisions, filter for clusters $\ge 50$, and enforce 70/30 time-based splits.
* **Phase 3 (Days 4–5): Synthesis Engine & Sandbox Evaluator**
  * Construct frontier LLM prompts with the `"unsure"` contract.
  * Implement zero-network subprocess sandbox enforcing the $\ge 98\%$ agreement rule.
  * Evaluate top habits (`extract_pnr`, `extract_user_id`, `traversal_loop`).
* **Phase 4 (Day 6): Baseline Benchmarks**
  * Score against Semantic Cache and Calibrated Classifier baselines.
  * Compile leaderboard metrics: Coverage % vs. Tokens Saved per 1k decisions.
* **Phase 5 (Day 7): Visual Dashboard & Interceptor Packaging**
  * Generate `dashboard.html` rendering the 30-day "lit up" agent workload map.
  * Finalize the runtime interceptor hook for deployment.
