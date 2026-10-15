"""agent.py -- Part D: Grounded Policy RAG and ReAct Support Refund Agent.

Tasks:
1. Document chunking (40 words, 10 overlap).
2. TF-IDF retrieval with cosine similarity.
3. Grounded Q&A with POLICY ASSISTANT prompt.
4. Retrieval & grounding evaluation on policy_eval.csv (10 overlap vs. 0 overlap).
5. Tool specifications and execution map against data/instamart.db.
6. ReAct loop with limits (max_iterations, token_limit, timeout).
7. Execution over all 7 scenarios in agent_scenarios.csv -> outputs/agent_runs.jsonl & outputs/refund_ledger.jsonl.
8. Crash-and-resume checkpointing in state/.
"""

import os
import sys
import json
import time
import random
import re
import sqlite3
from datetime import datetime
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

sys.path.insert(0, os.path.abspath("."))
import mock_llm

POLICIES_DIR = "data/policies"
DB_PATH = "data/instamart.db"
OUTPUT_DIR = "outputs"
STATE_DIR = "state"
LEDGER_PATH = os.path.join(OUTPUT_DIR, "refund_ledger.jsonl")
RUNS_PATH = os.path.join(OUTPUT_DIR, "agent_runs.jsonl")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


# ==============================================================================
# Task 1: Document Chunking
# ==============================================================================
def chunk_document(filepath: str, chunk_size: int = 40, overlap: int = 10) -> list[str]:
    """Splits a document into word chunks of chunk_size with given overlap.
    Stops after the first chunk whose end reaches or passes the last word.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        words = f.read().split()
    if not words:
        return []
    step = chunk_size - overlap
    chunks = []
    i = 0
    while True:
        chunk_words = words[i : i + chunk_size]
        chunks.append(" ".join(chunk_words))
        if i + chunk_size >= len(words):
            break
        i += step
    return chunks


def load_and_chunk_all_policies(policies_dir: str = POLICIES_DIR, chunk_size: int = 40, overlap: int = 10) -> list[dict]:
    all_chunks = []
    for fname in sorted(os.listdir(policies_dir)):
        if fname.endswith(".txt"):
            fpath = os.path.join(policies_dir, fname)
            chunks = chunk_document(fpath, chunk_size=chunk_size, overlap=overlap)
            for c in chunks:
                all_chunks.append({"source": fname, "text": c})
    return all_chunks


# ==============================================================================
# Task 2 & 3: TF-IDF Retrieval & Grounded Q&A
# ==============================================================================
class PolicyRetriever:
    def __init__(self, chunk_size: int = 40, overlap: int = 10):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks = load_and_chunk_all_policies(chunk_size=chunk_size, overlap=overlap)
        self.vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.vectorizer.fit_transform([c["text"] for c in self.chunks])

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.tfidf_matrix).flatten()
        top_indices = sims.argsort()[::-1][:k]
        return [
            {"source": self.chunks[i]["source"], "score": float(sims[i]), "text": self.chunks[i]["text"]}
            for i in top_indices
        ]

    def answer(self, question: str, k: int = 3) -> tuple[str, list[str]]:
        retrieved = self.retrieve(question, k=k)
        context_blocks = "\n".join([f"[{r['source']}]\n{r['text']}" for r in retrieved])
        messages = [
            {
                "role": "system",
                "content": "POLICY ASSISTANT. Answer the question using only the supplied context. "
                           "If you could not find the information in the policy documents, say so."
            },
            {
                "role": "user",
                "content": f"CONTEXT:\n{context_blocks}\nQUESTION:\n{question}"
            }
        ]
        resp = mock_llm.chat(messages)
        return resp.choices[0].message.content, [r["source"] for r in retrieved]


# Initialize global default retriever
default_retriever = PolicyRetriever(chunk_size=40, overlap=10)


# ==============================================================================
# Task 5: Tool Specifications and Implementations
# ==============================================================================
def get_order(order_id: str) -> dict:
    """Reads data/instamart.db orders table."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT order_id, status, order_amount, delivery_minutes FROM orders WHERE order_id = ?",
            (order_id,)
        )
        row = cur.fetchone()
        if not row:
            return {"error": "order not found"}
        return {
            "order_id": row[0],
            "status": row[1],
            "order_amount": float(row[2]),
            "delivery_minutes": float(row[3]) if row[3] is not None else None
        }
    finally:
        conn.close()


def search_policy(query: str) -> dict:
    """Retrieves policy chunks using TF-IDF."""
    return {"results": default_retriever.retrieve(query, k=3)}


def calculate_refund(order_amount: float, delivery_minutes: float) -> dict:
    """Computes refund amount following quick-commerce rules."""
    if delivery_minutes is not None and delivery_minutes > 45:
        return {"refund_inr": float(order_amount)}
    return {"refund_inr": 0.0}


def issue_refund(order_id: str, refund_inr: float) -> dict:
    """Appends issued refund to outputs/refund_ledger.jsonl."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "tool": "issue_refund",
        "order_id": order_id,
        "refund_inr": float(refund_inr)
    }
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"refund_inr": float(refund_inr)}


def escalate_to_human(order_id: str, refund_inr: float) -> dict:
    """Appends escalation to outputs/refund_ledger.jsonl."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "tool": "escalate_to_human",
        "order_id": order_id,
        "refund_inr": float(refund_inr)
    }
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return {"refund_inr": float(refund_inr)}


TOOL_MAP = {
    "get_order": get_order,
    "search_policy": search_policy,
    "calculate_refund": calculate_refund,
    "issue_refund": issue_refund,
    "escalate_to_human": escalate_to_human
}

TOOLS_SPEC = [
    {
        "name": "get_order",
        "description": "Look up an order in the database by its order ID.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"]
        }
    },
    {
        "name": "search_policy",
        "description": "Search the refund and delivery policies using a keyword query.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        }
    },
    {
        "name": "calculate_refund",
        "description": "Calculate eligible refund in INR based on order amount and delivery duration.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_amount": {"type": "number"},
                "delivery_minutes": {"type": "number"}
            },
            "required": ["order_amount", "delivery_minutes"]
        }
    },
    {
        "name": "issue_refund",
        "description": "Issue approved refund for orders delivered late and below INR 1000.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "refund_inr": {"type": "number"}
            },
            "required": ["order_id", "refund_inr"]
        }
    },
    {
        "name": "escalate_to_human",
        "description": "Escalate high-value refunds exceeding INR 1000 to a human support lead.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "refund_inr": {"type": "number"}
            },
            "required": ["order_id", "refund_inr"]
        }
    }
]


# ==============================================================================
# Task 6 & 7 & 8: ReAct Loop, Safe Fallbacks & Resumability
# ==============================================================================
def run_agent(
    user_message: str,
    scenario_id: str,
    max_iterations: int = 6,
    token_limit: int = 6000,
    time_limit_seconds: float = 10.0,
    run_id: str | None = None,
    checkpoint_state: dict | None = None,
    simulate_crash_after_step: int | None = None
) -> dict:
    """Executes the ReAct loop with iteration limits, token budgets, timeouts, and checkpointing."""
    start_time = time.monotonic()
    if run_id is None:
        run_id = f"run_{scenario_id}_{int(time.time() * 1000)}"

    if checkpoint_state is not None:
        messages = checkpoint_state["messages"]
        tokens_used = checkpoint_state["tokens_used"]
        llm_calls = checkpoint_state.get("llm_calls", 0)
        steps = checkpoint_state["steps"]
        tools_executed = checkpoint_state["tools_executed"]
    else:
        messages = [
            {"role": "system", "content": "You are a customer refund support AGENT. Use the available tools to verify orders, evaluate policies, and process refunds."},
            {"role": "user", "content": user_message}
        ]
        tokens_used = 0
        llm_calls = 0
        steps = []
        tools_executed = []

    status = None
    final_answer = None

    for iteration in range(len(tools_executed), max_iterations):
        # (c) Timeout limit check at the top of iteration
        elapsed = time.monotonic() - start_time
        if elapsed >= time_limit_seconds:
            status = "FALLBACK_TIMEOUT"
            final_answer = "TIMEOUT: Agent execution time limit exceeded. Handing over to human support."
            break

        # Call chat API
        resp = mock_llm.chat(messages, tools=TOOLS_SPEC)
        llm_calls += 1
        msg = resp.choices[0].message
        usage_tok = resp.usage.total_tokens

        # (b) Token limit check after model call
        if tokens_used + usage_tok > token_limit:
            tokens_used += usage_tok
            status = "FALLBACK_TOKEN_LIMIT"
            final_answer = "TOKEN_LIMIT: Agent exceeded token budget. Handing over to human support."
            break

        tokens_used += usage_tok

        # If model did not request tool calls -> final answer
        if not msg.tool_calls:
            final_answer = msg.content
            if ":" in final_answer:
                status = final_answer.split(":")[0].strip()
            else:
                status = "COMPLETED"
            break

        # Process tool call
        tc = msg.tool_calls[0]
        tool_id = tc.id
        tool_name = tc.name
        tool_args = tc.arguments

        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": tool_id, "name": tool_name, "arguments": tool_args}]
        })

        # Execute tool
        func = TOOL_MAP.get(tool_name)
        if not func:
            tool_obs = {"error": f"Tool {tool_name} not found"}
        else:
            tool_obs = func(**tool_args)

        tools_executed.append(tool_name)
        steps.append({
            "step": len(tools_executed),
            "tool_name": tool_name,
            "arguments": tool_args,
            "observation": tool_obs
        })

        messages.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "name": tool_name,
            "content": json.dumps(tool_obs)
        })

        # Save checkpoint in state/
        checkpoint = {
            "run_id": run_id,
            "scenario_id": scenario_id,
            "messages": messages,
            "tokens_used": tokens_used,
            "llm_calls": llm_calls,
            "steps": steps,
            "tools_executed": tools_executed
        }
        ckpt_path = os.path.join(STATE_DIR, f"{run_id}.json")
        with open(ckpt_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2)

        # Simulation of crash for Task 8
        if simulate_crash_after_step is not None and len(tools_executed) == simulate_crash_after_step:
            raise RuntimeError(f"Simulated crash after tool step {simulate_crash_after_step}")

    # (a) Max iterations fallback
    if status is None:
        status = "FALLBACK_MAX_ITERATIONS"
        final_answer = "MAX_ITERATIONS: Agent reached step limit without final resolution. Handing over to human support."

    return {
        "run_id": run_id,
        "scenario_id": scenario_id,
        "status": status,
        "final_answer": final_answer,
        "steps": steps,
        "llm_calls": llm_calls,
        "tokens_used": tokens_used
    }


def resume_agent(run_id: str, max_iterations: int = 6, token_limit: int = 6000, time_limit_seconds: float = 10.0) -> dict:
    """Loads checkpoint from state/{run_id}.json and resumes execution."""
    ckpt_path = os.path.join(STATE_DIR, f"{run_id}.json")
    if not os.path.exists(ckpt_path):
        raise FileNotFoundError(f"Checkpoint not found at {ckpt_path}")
    with open(ckpt_path, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)

    # Reconstruct user message from messages
    user_msg = next(m["content"] for m in checkpoint["messages"] if m["role"] == "user")
    return run_agent(
        user_message=user_msg,
        scenario_id=checkpoint["scenario_id"],
        max_iterations=max_iterations,
        token_limit=token_limit,
        time_limit_seconds=time_limit_seconds,
        run_id=run_id,
        checkpoint_state=checkpoint
    )


# ==============================================================================
# Pipeline Execution & Reporting
# ==============================================================================
def main():
    print("=" * 80)
    print("TASK 1, 2, 3 & 4: DOCUMENT CHUNKING, RETRIEVAL & POLICY GROUNDING")
    print("=" * 80)

    # 1. Chunking summary
    chunk_counts = {}
    for fname in sorted(os.listdir(POLICIES_DIR)):
        if fname.endswith(".txt"):
            fpath = os.path.join(POLICIES_DIR, fname)
            c = chunk_document(fpath, chunk_size=40, overlap=10)
            chunk_counts[fname] = len(c)
    total_c = sum(chunk_counts.values())
    print("Document Chunk Counts (40 words, 10 overlap):")
    for doc, cnt in chunk_counts.items():
        print(f"  - {doc}: {cnt} chunks")
    print(f"  Total Chunks: {total_c} (Reference: 15 — refund 4, delivery 3, escalation 3, payment 3, privacy 2)\n")

    # 2. Retrieval demonstration
    top3_demo = default_retriever.retrieve("refund policy late delivery", k=3)
    print("Top 3 retrieved chunks for query 'refund policy late delivery':")
    for r in top3_demo:
        print(f"  - {r['source']} (Score: {r['score']:.4f})")
    all_from_refund = all(r["source"] == "refund_policy.txt" for r in top3_demo)
    print(f"Verification: Top 3 all from refund_policy.txt -> {all_from_refund}\n")

    # 3. Grounding evaluation on policy_eval.csv
    eval_df = pd.read_csv("data/raw/policy_eval.csv")
    doc_hits = 0
    fact_hits = 0
    unanswerable_hits = 0

    print("Evaluating 14 Questions (Overlap = 10 words):")
    eval_rows = []
    for idx, row in eval_df.iterrows():
        qid = f"Q{idx+1}"
        q = row["question"]
        exp_doc = row["expected_doc"]
        exp_fact = row["expected_fact"]
        ans_text, sources = default_retriever.answer(q)

        is_unanswerable = (exp_doc == "NONE")
        if not is_unanswerable:
            hit_d = exp_doc in sources
            hit_f = exp_fact in ans_text
            if hit_d:
                doc_hits += 1
            if hit_f:
                fact_hits += 1
            eval_rows.append({"Question": qid, "Type": "Answerable", "Expected Doc": exp_doc, "Doc Hit": hit_d, "Fact Hit": hit_f})
        else:
            hit_fb = ans_text.startswith("I could not find")
            if hit_fb:
                unanswerable_hits += 1
            eval_rows.append({"Question": qid, "Type": "Unanswerable", "Expected Doc": "NONE", "Doc Hit": "N/A", "Fact Hit": hit_fb})

    print(pd.DataFrame(eval_rows).to_string(index=False))
    print(f"\nGrounding Evaluation Summary (Overlap = 10):")
    print(f"  - Expected Doc in Top 3: {doc_hits}/12 (Reference: 12/12)")
    print(f"  - Expected Fact Contained: {fact_hits}/12 (Reference: 12/12)")
    print(f"  - Unanswerable Fallback: {unanswerable_hits}/2 (Reference: 2/2)\n")

    # 4. Zero overlap evaluation (Overlap = 0)
    zero_retriever = PolicyRetriever(chunk_size=40, overlap=0)
    zero_fact_hits = 0
    failed_q = []
    for idx, row in eval_df.iterrows():
        qid = f"Q{idx+1}"
        q = row["question"]
        exp_doc = row["expected_doc"]
        exp_fact = row["expected_fact"]
        if exp_doc != "NONE":
            ans_text, _ = zero_retriever.answer(q)
            if exp_fact in ans_text:
                zero_fact_hits += 1
            else:
                failed_q.append((qid, q, exp_fact, ans_text))

    print(f"Zero-Overlap Evaluation (Overlap = 0 words):")
    print(f"  - Fact Hits: {zero_fact_hits}/12 (Reference: < 12, at least one question fails)")
    print("  Failed Questions due to Boundary Splits:")
    for f in failed_q:
        print(f"    * {f[0]}: '{f[1]}'\n      Expected Fact: '{f[2]}'\n      Actual Answer: '{f[3]}'")

    print("\n" + "=" * 80)
    print("TASK 6: REACT AGENT SCENARIOS (data/raw/agent_scenarios.csv)")
    print("=" * 80)

    # Clean existing ledger, runs, and state files for a clean run
    if os.path.exists(LEDGER_PATH):
        os.remove(LEDGER_PATH)
    if os.path.exists(RUNS_PATH):
        os.remove(RUNS_PATH)
    if os.path.exists("state"):
        for sf in os.listdir("state"):
            if sf.endswith(".json"):
                os.remove(os.path.join("state", sf))

    scenarios = pd.read_csv("data/raw/agent_scenarios.csv")
    scenario_results = []

    for _, row in scenarios.iterrows():
        sid = row["scenario_id"]
        cid = row["customer_id"]
        msg = row["message"]
        exp_out = row["expected_outcome"]
        exp_ref = float(row["expected_refund_inr"])

        mock_llm.reset()
        res = run_agent(msg, sid)

        # Extract refund amount from tool observation or arguments
        amt_val = 0.0
        for step in res["steps"]:
            if "refund_inr" in step["observation"]:
                amt_val = float(step["observation"]["refund_inr"])
            elif "refund_inr" in step["arguments"]:
                amt_val = float(step["arguments"]["refund_inr"])

        scenario_results.append({
            "scenario_id": sid,
            "status": res["status"],
            "expected_outcome": exp_out,
            "refund_amount": amt_val,
            "expected_refund": exp_ref,
            "llm_calls": res["llm_calls"],
            "tokens_used": res["tokens_used"],
            "final_answer": res["final_answer"]
        })

        # Append to outputs/agent_runs.jsonl
        run_record = {
            "scenario_id": sid,
            "status": res["status"],
            "final_answer": res["final_answer"],
            "llm_calls": res["llm_calls"],
            "tokens_used": res["tokens_used"],
            "steps": res["steps"]
        }
        with open(RUNS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(run_record) + "\n")

    df_scen = pd.DataFrame(scenario_results)
    disp_cols = ["scenario_id", "status", "refund_amount", "llm_calls", "tokens_used"]
    print("\nSeven Scenario Results Table:")
    print(df_scen[disp_cols].to_string(index=False))

    print("\n" + "=" * 80)
    print("TASK 7: STOP SAFELY DEMONSTRATIONS (LIMITS & TIMEOUT)")
    print("=" * 80)

    s1_msg = scenarios.loc[scenarios["scenario_id"] == "S1", "message"].iloc[0]

    # Token Limit Demo: S1 with token_limit = 200
    mock_llm.reset()
    res_token_demo = run_agent(s1_msg, "S1_token_demo", token_limit=200)
    print(f"Token Limit Demonstration (token_limit=200):")
    print(f"  - Status:       {res_token_demo['status']}")
    print(f"  - Tokens Used:  {res_token_demo['tokens_used']}")
    print(f"  - Final Answer: {res_token_demo['final_answer']}")

    # Timeout Demo: S1 with time_limit_seconds = 0.0
    mock_llm.reset()
    res_time_demo = run_agent(s1_msg, "S1_timeout_demo", time_limit_seconds=0.0)
    print(f"\nTimeout Demonstration (time_limit_seconds=0.0):")
    print(f"  - Status:       {res_time_demo['status']}")
    print(f"  - LLM Calls:    {res_time_demo['llm_calls']}")
    print(f"  - Final Answer: {res_time_demo['final_answer']}")

    print("\n" + "=" * 80)
    print("TASK 8: RESUMABILITY DEMONSTRATION (CRASH & RESUME ON S1)")
    print("=" * 80)

    crash_run_id = f"s1_crash_resume_{int(time.time())}"
    mock_llm.reset()

    # Part 1: Run until step 2 then simulate crash
    print(f"Phase 1: Starting run {crash_run_id} with simulated crash after Step 2...")
    try:
        run_agent(s1_msg, "S1", run_id=crash_run_id, simulate_crash_after_step=2)
    except RuntimeError as err:
        print(f"  -> Successfully intercepted simulated crash: '{err}'")

    # Part 2: Resume from checkpoint
    print(f"Phase 2: Calling resume_agent('{crash_run_id}')...")
    resumed_run = resume_agent(crash_run_id)

    tool_seq = [s["tool_name"] for s in resumed_run["steps"]]
    print(f"Resumed Run Outcome:")
    print(f"  - Final Status: {resumed_run['status']}")
    print(f"  - Final Answer: {resumed_run['final_answer']}")
    print(f"  - Tools Executed ({len(tool_seq)}): {' -> '.join(tool_seq)}")
    assert tool_seq == ["get_order", "search_policy", "calculate_refund", "issue_refund"], "Tool sequence mismatch!"
    assert resumed_run["status"] == "REFUND", "Final status mismatch!"
    print("Resumability Assertion: EXACT MATCH (4 distinct tools executed, zero repeated, final status REFUND).")


if __name__ == "__main__":
    main()
