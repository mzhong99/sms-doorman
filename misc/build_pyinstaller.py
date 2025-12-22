from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import tomllib  # Python 3.11+

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "pyproject.toml"
WRAPPERS = ROOT / ".pyi_wrappers"

def _safe_name(name: str) -> str:
    # conservative: allow alnum, dash, underscore
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name)

def main() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    scripts = data.get("tool", {}).get("poetry", {}).get("scripts", {})
    if not scripts:
        raise SystemExit("No [tool.poetry.scripts] found in pyproject.toml")

    WRAPPERS.mkdir(parents=True, exist_ok=True)

    for script_name, target in scripts.items():
        # target like "pkg.module:func"
        if ":" not in target:
            raise SystemExit(f"Unsupported script target (expected module:callable): {script_name} = {target}")
        module, func = target.split(":", 1)

        out_name = _safe_name(script_name)
        wrapper = WRAPPERS / f"{out_name}.py"
        wrapper.write_text(
            f"""\
from {module} import {func} as _entry

if __name__ == "__main__":
    raise SystemExit(_entry())
""",
            encoding="utf-8",
        )

        cmd = [
            "pyinstaller",
            "--clean",
            "--onefile",
            "--name",
            script_name,
            str(wrapper),
        ]
        print("+", " ".join(cmd))
        subprocess.check_call(cmd, cwd=str(ROOT), env=os.environ.copy())

if __name__ == "__main__":
    main()

