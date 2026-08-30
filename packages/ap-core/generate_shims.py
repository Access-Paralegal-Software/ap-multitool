import os
from pathlib import Path

src_dir = Path(__file__).parent / "src" / "ap_core"
dst_dir = Path(__file__).parent / "src" / "core"

dst_dir.mkdir(parents=True, exist_ok=True)
(dst_dir / "operations").mkdir(parents=True, exist_ok=True)

for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith(".py"):
            rel = Path(root).relative_to(src_dir)
            target_dir = dst_dir / rel
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / f
            
            mod_parts = list(rel.parts)
            stem = Path(f).stem
            if stem != "__init__":
                mod_parts.append(stem)
            
            if mod_parts:
                mod_name = ".".join(mod_parts)
                if mod_name == "operations":
                    operation_modules = sorted(
                        path.stem
                        for path in (src_dir / "operations").glob("*.py")
                        if path.stem != "__init__"
                    )
                    module_names = ",\n    ".join(repr(name) for name in operation_modules)
                    target_file.write_text(
                        "import sys as _sys\n"
                        "from importlib import import_module as _import_module\n\n"
                        "from ap_core.operations import *\n\n"
                        "for _name in (\n"
                        f"    {module_names},\n"
                        "):\n"
                        "    _sys.modules[f\"{__name__}.{_name}\"] = "
                        "_import_module(f\"ap_core.operations.{_name}\")\n",
                        encoding="utf-8",
                    )
                else:
                    target_file.write_text(
                        "import sys as _sys\n"
                        "from importlib import import_module as _import_module\n\n"
                        f"_sys.modules[__name__] = _import_module(\"ap_core.{mod_name}\")\n",
                        encoding="utf-8",
                    )
            else:
                target_file.write_text(
                    "from ap_core import *\n"
                    "from ap_core import __channel__, __version__\n",
                    encoding="utf-8",
                )

print("Generated core shim files successfully.")
