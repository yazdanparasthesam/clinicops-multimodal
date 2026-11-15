import pathlib, sys
sys.path.insert(0, "app")
from app.main import app
import json, yaml, pathlib
openapi = app.openapi()
path = pathlib.Path("../openapi.yaml")
# if run inside backend, path is backend/../openapi.yaml -> root
if not path.exists():
    path = pathlib.Path("../../openapi.yaml")
if not path.exists():
    path = pathlib.Path("./openapi.yaml")
    if str(path).endswith("backend/openapi.yaml"):
        path = pathlib.Path("../openapi.yaml")
# Fallback to repo root
for candidate in [pathlib.Path("openapi.yaml"), pathlib.Path("../openapi.yaml"), pathlib.Path("../../openapi.yaml")]:
    if candidate.parent.exists():
        pass
# Write to wherever invoked via Makefile: backend/scripts -> backend/../openapi.yaml should be repo
# We explicitly write to repo root if possible
candidates = [pathlib.Path("../openapi.yaml"), pathlib.Path("../../openapi.yaml"), pathlib.Path("openapi.yaml")]
for c in candidates:
    try:
        import yaml as y
        with open(c, "w") as f:
            y.safe_dump(openapi, f, sort_keys=False)
        print(f"Wrote {c}")
        break
    except Exception as e:
        continue
