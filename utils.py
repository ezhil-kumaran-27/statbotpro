"""
utils.py — StatBot Pro
Helper utilities: CSV loading, chart management, safe execution, formatting.
"""

import io
import traceback
import uuid
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CHART_DIR = Path(__file__).parent / "static" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)


# ── CSV Loading ───────────────────────────────────────────────────────────────

def load_csv(file_obj) -> pd.DataFrame:
    """
    Load CSV from a file-like object.
    Auto-detects encoding and handles common CSV variants.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
    last_err = None

    for enc in encodings:
        try:
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)
            df = pd.read_csv(file_obj, encoding=enc)
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            # Try to parse obvious date columns (but NOT year columns, which should stay as integers)
            for col in df.columns:
                if any(kw in col.lower() for kw in ["date", "time", "datetime"]):
                    try:
                        df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                    except Exception:
                        pass
            return df
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            last_err = exc

    raise ValueError(f"Could not read CSV. Error: {last_err}")

# ── DataFrame Summary ─────────────────────────────────────────────────────────

def dataframe_summary(df: pd.DataFrame) -> str:
    """Return a human-readable summary of the DataFrame."""
    lines = [
        f"Shape: {df.shape[0]:,} rows × {df.shape[1]} columns",
        "",
        "Columns:",
    ]
    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isna().sum()
        null_str = f"  [{nulls:,} missing]" if nulls > 0 else ""
        if pd.api.types.is_numeric_dtype(df[col]):
            mn, mx, mean = df[col].min(), df[col].max(), df[col].mean()
            lines.append(f"  • {col!r} ({dtype}){null_str} — range [{mn:.2g} → {mx:.2g}], mean={mean:.2g}")
        elif hasattr(df[col], "dt"):
            lines.append(f"  • {col!r} (datetime){null_str}")
        else:
            n_unique = df[col].nunique()
            top = df[col].value_counts().index[0] if len(df[col].dropna()) > 0 else "N/A"
            lines.append(f"  • {col!r} ({dtype}){null_str} — {n_unique} unique, top: '{top}'")
    return "\n".join(lines)


# ── Chart helpers ─────────────────────────────────────────────────────────────

def save_current_figure() -> tuple[str, bytes]:
    """
    Save the active Matplotlib figure to disk + return as bytes.
    Returns (filepath_str, png_bytes).
    """
    filename = f"chart_{uuid.uuid4().hex[:8]}.png"
    filepath = CHART_DIR / filename

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.savefig(str(filepath), dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close("all")

    buf.seek(0)
    return str(filepath), buf.read()


def close_all_figures() -> None:
    plt.close("all")


# ── Safe Code Execution ───────────────────────────────────────────────────────

def safe_exec(code: str, namespace: dict) -> dict:
    """
    Execute code string in the given namespace dict.
    Returns the updated namespace. Raises RuntimeError on failure.
    """
    try:
        compiled = compile(code, "<statbot_generated>", "exec")
        exec(compiled, namespace)  # noqa: S102
    except Exception:
        raise RuntimeError(traceback.format_exc())
    return namespace


# ── Result Formatting ─────────────────────────────────────────────────────────

def format_result(value) -> str:
    """Convert any Python value to a clean string for display."""
    if isinstance(value, pd.DataFrame):
        if len(value) > 50:
            return value.head(50).to_string(index=True) + f"\n... ({len(value):,} total rows)"
        return value.to_string(index=True)
    if isinstance(value, pd.Series):
        return value.to_string()
    if isinstance(value, (list, tuple)):
        return "\n".join(str(v) for v in value)
    return str(value)
