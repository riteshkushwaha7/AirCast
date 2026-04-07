import sys
from pathlib import Path


def _bootstrap_pipeline_path() -> None:
    pipeline_root = Path(__file__).resolve().parents[1]
    if str(pipeline_root) not in sys.path:
        sys.path.insert(0, str(pipeline_root))


_bootstrap_pipeline_path()
