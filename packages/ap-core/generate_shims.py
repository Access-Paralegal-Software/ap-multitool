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
                target_file.write_text(f"from ap_core.{mod_name} import *\n", encoding="utf-8")
            else:
                target_file.write_text("from ap_core import *\n", encoding="utf-8")

print("Generated core shim files successfully.")
