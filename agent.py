"""
agent.py — StatBot Pro
LLM-powered autonomous analysis pipeline:
  question → context building → LLM code gen → security check → exec → result
"""

from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import math, statistics, datetime, collections, io, base64, json, string

from security import SecurityError, validate_code
from utils import safe_exec, save_current_figure, close_all_figures, format_result

# ── Result dataclass ──────────────────────────────────────────────────────────
@dataclass
class AgentResult:
    answer: str = ""
    code: str = ""
    chart_path: Optional[str] = None
    chart_bytes: Optional[bytes] = None
    error: Optional[str] = None
    success: bool = True

# ── Prompt Template ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = textwrap.dedent("""
You are StatBot Pro, an expert Python data analyst.
You are given a pandas DataFrame already loaded as variable `df`.

Your task: Write a SINGLE self-contained Python code block that answers the user's question.

RULES — follow every rule exactly:
1. Use ONLY the existing `df` variable. Do NOT reload any file.
2. Available libraries (pre-imported, use directly): pd, np, plt, math, statistics, datetime, json, collections, io, base64, string, re.
3. NEVER import: os, sys, subprocess, shutil, socket, urllib, requests, pickle, threading, importlib, ctypes, eval, exec.
4. Apply plt.style.use('seaborn-v0_8-whitegrid') for all charts.
5. Set informative chart titles, axis labels, and legends.
6. Use plt.figure(figsize=(10, 5)) or appropriate size for charts.
7. ALWAYS assign a final answer string to the variable ANSWER.
   - For numerical results: format numbers clearly with units/context.
   - For DataFrames/Series: assign them as strings using .to_string().
   - For charts: set ANSWER = "Chart generated successfully. [brief description]"
   - If question can't be answered: ANSWER = "I could not find the data needed to answer this question."
8. Handle missing values, empty DataFrames, and type mismatches gracefully with try/except.
9. Use df['Column Name'] syntax (columns may have spaces).
10. For date/time columns, use pd.to_datetime() if needed before plotting.
11. For bar/line charts with many categories, limit to top 15 for readability.
12. Use professional colors: ['#2563EB','#0891B2','#059669','#D97706','#DC2626','#7C3AED'] for multi-series.
13. Do NOT print anything — only set the ANSWER variable and optionally create a plt figure.

Respond with ONLY one ```python ... ``` code block. No explanations outside it.
""").strip()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_code(llm_text: str) -> str:
    """Extract the first ```python ... ``` block from the LLM response."""
    match = re.search(r"```python\s*(.*?)```", llm_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: strip any ``` fences
    cleaned = re.sub(r"```\w*", "", llm_text).strip("` \n")
    return cleaned


def _df_context(df: pd.DataFrame, max_rows: int = 3) -> str:
    """Build a concise description of the DataFrame for the prompt."""
    lines = [
        f"DataFrame shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
        f"Columns: {list(df.columns)}",
        "",
        "Column details (name → dtype, sample values):",
    ]
    for col in df.columns:
        dtype = df[col].dtype
        samples = df[col].dropna().head(3).tolist()
        lines.append(f"  '{col}' → {dtype}  |  samples: {samples}")

    lines += [
        "",
        f"First {max_rows} rows:",
        df.head(max_rows).to_string(index=False),
        "",
        "Numeric summary:",
        df.describe(include="number").round(2).to_string(),
    ]
    return "\n".join(lines)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_agent(
    df: pd.DataFrame,
    question: str,
    api_fn: Callable[[str, str], str],
) -> AgentResult:
    """
    Full pipeline:
    1. Build context from df
    2. Call LLM to generate code
    3. Security validate the code
    4. Execute safely
    5. Extract ANSWER and optional chart
    """
    result = AgentResult()


    # ── Step 1: Build prompt ──────────────────────────────────────────────────
    ctx = _df_context(df)
    user_msg = f"Question: {question}\n\nDataFrame Info:\n{ctx}"


    # ── Step 2: Call LLM ──────────────────────────────────────────────────────
    try:
        llm_reply = api_fn(SYSTEM_PROMPT, user_msg)
    except Exception as exc:
        result.success = False
        result.error = f"API Error: {exc}"
        return result

    # ── Step 3: Extract code ──────────────────────────────────────────────────
    code = _extract_code(llm_reply)
    result.code = code

    if not code:
        result.success = False
        result.error = "The model did not return a code block. Try rephrasing your question."
        return result

    # ── Step 4: Security check ────────────────────────────────────────────────
    try:
        validate_code(code)
    except SecurityError as exc:
        result.success = False
        result.error = str(exc)
        return result

    # ── Step 5: Execute ───────────────────────────────────────────────────────
    close_all_figures()

    # Build safe execution namespace
    namespace = {
        # Core data
        "df": df.copy(),
        # Libraries
        "pd": pd,
        "np": np,
        "plt": plt,
        "math": math,
        "statistics": statistics,
        "datetime": datetime,
        "json": json,
        "collections": collections,
        "io": io,
        "base64": base64,
        "string": string,
        "re": re,
        # Result placeholder
        "ANSWER": "",
    }

    try:
        namespace = safe_exec(code, namespace)
    except RuntimeError as exc:
        result.success = False
        result.error = f"Execution error:\n{exc}"
        return result

    # ── Step 6: Extract results ───────────────────────────────────────────────
    raw_answer = namespace.get("ANSWER", "")
    result.answer = format_result(raw_answer) if raw_answer else "(No ANSWER variable was set by the code.)"

    # Check if a chart was produced
    if plt.get_fignums():
        try:
            path, png_bytes = save_current_figure()
            result.chart_path = path
            result.chart_bytes = png_bytes
        except Exception as exc:
            result.error = f"Chart save warning: {exc}"
    else:
        close_all_figures()

    return result
