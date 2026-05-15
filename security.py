"""
security.py — StatBot Pro
Validates generated code before execution using regex + AST scanning.
"""
import re
import ast

# ── Banned regex patterns ──────────────────────────────────────────────────────
BANNED_PATTERNS = [
    (r"\bos\.system\b",          "os.system() is not allowed"),
    (r"\bos\.popen\b",           "os.popen() is not allowed"),
    (r"\bos\.remove\b",          "os.remove() is not allowed"),
    (r"\bos\.unlink\b",          "os.unlink() is not allowed"),
    (r"\bos\.rmdir\b",           "os.rmdir() is not allowed"),
    (r"\bos\.makedirs\b",        "os.makedirs() is not allowed"),
    (r"\bshutil\b",              "shutil module is not allowed"),
    (r"\bsubprocess\b",          "subprocess module is not allowed"),
    (r"\b__import__\s*\(",       "__import__() is not allowed"),
    (r"\beval\s*\(",             "eval() is not allowed"),
    (r"\bexec\s*\(",             "exec() is not allowed"),
    (r"\bopen\s*\([^)]*['\"][wa]['\"]", "open() in write/append mode is not allowed"),
    (r"\bchmod\b",               "chmod is not allowed"),
    (r"\bchown\b",               "chown is not allowed"),
    (r"\bsocket\b",              "socket module is not allowed"),
    (r"\burllib\b",              "urllib module is not allowed"),
    (r"\brequests\b",            "requests module is not allowed"),
    (r"\bhttpx\b",               "httpx module is not allowed"),
    (r"\bpickle\b",              "pickle module is not allowed"),
    (r"\bimportlib\b",           "importlib is not allowed"),
    (r"\bctypes\b",              "ctypes is not allowed"),
    (r"\bmultiprocessing\b",     "multiprocessing is not allowed"),
    (r"\bthreading\b",           "threading is not allowed"),
    (r"\bpty\b",                 "pty is not allowed"),
    (r"\bsignal\b",              "signal module is not allowed"),
    (r"rm\s+-rf",                "rm -rf is not allowed"),
    (r"\bgetattr\s*\([^)]*__",  "getattr with dunder attributes is not allowed"),
]


# ── Allowed imports ───────────────────────────────────────────────────────────
SAFE_MODULES = {
    "pandas", "pd", "numpy", "np",
    "matplotlib", "matplotlib.pyplot", "matplotlib.ticker",
    "matplotlib.dates", "matplotlib.patches",
    "plt", "math", "statistics", "datetime", "re",
    "json", "collections", "itertools", "functools",
    "io", "base64", "string", "random",
}


class SecurityError(Exception):
    pass

def validate_code(code: str) -> None:
    """
    Run regex and AST checks. Raises SecurityError if anything is blocked.
    Call this before executing any LLM-generated code.
    """
    # 1. Regex scan
    for pattern, message in BANNED_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            raise SecurityError(f"🚫 Security blocked: {message}")


    # 2. AST import scan
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise SecurityError(f"Syntax error in generated code: {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in SAFE_MODULES:
                    raise SecurityError(
                        f"🚫 Import blocked: '{alias.name}' is not in the safe list."
                    )

        if isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in SAFE_MODULES:
                raise SecurityError(
                    f"🚫 Import blocked: 'from {node.module} import ...' is not allowed."
                )
