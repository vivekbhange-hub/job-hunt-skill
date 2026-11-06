"""Load helper scripts by path. Skill folders contain hyphens, so normal imports fail."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_script(skill, filename):
    path = ROOT / "skills" / skill / filename
    name = "jobhunt_" + path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
