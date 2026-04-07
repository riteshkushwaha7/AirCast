import os
import sys
from pathlib import Path


def _bootstrap_backend_path() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    if str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))


_bootstrap_backend_path()

os.environ["DEBUG"] = "true"
os.environ["SOURCE_MOCK_MODE"] = "true"
