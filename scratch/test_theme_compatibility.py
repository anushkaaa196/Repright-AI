"""Theme Compatibility and Static Audit Suite for REPRIGHT AI.

Scans the entire codebase using AST parsing to verify that every `theme.<ATTR>`
reference corresponds to a valid, defined attribute inside `ui.theme`.
Prevents runtime AttributeError exceptions during UI startup and navigation.
"""

import ast
import glob
import sys
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import ui.theme as theme


def test_theme_compatibility():
    print("=" * 65)
    print("  REPRIGHT AI — THEME COMPATIBILITY & STATIC AUDIT SUITE")
    print("=" * 65)

    theme_attrs = set(dir(theme))
    missing = {}
    total_references = 0

    py_files = [
        f for f in glob.glob(str(Path(_ROOT) / "**" / "*.py"), recursive=True)
        if "venv" not in f and ".git" not in f
    ]

    for py_file in py_files:
        rel_path = Path(py_file).relative_to(_ROOT)
        with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
            try:
                tree = ast.parse(f.read(), filename=str(rel_path))
            except Exception as e:
                print(f"[WARN] Failed to parse {rel_path}: {e}")
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "theme":
                attr = node.attr
                total_references += 1
                if attr not in theme_attrs:
                    missing.setdefault(attr, []).append((str(rel_path), node.lineno))

    print(f"\nScanned {len(py_files)} project Python files.")
    print(f"Verified {total_references} `theme.*` attribute references.")

    if missing:
        print("\n❌ MISSING THEME ATTRIBUTES FOUND:")
        for attr, occurrences in sorted(missing.items()):
            print(f"\n  theme.{attr} (missing in ui.theme):")
            for fpath, lineno in occurrences:
                print(f"    • {fpath}:{lineno}")
        assert False, f"Found {len(missing)} missing theme attributes."

    print("\n✅ PASSED: 100% of `theme.*` constants exist in ui.theme.")
    print("=" * 65)
    return True


if __name__ == "__main__":
    test_theme_compatibility()
