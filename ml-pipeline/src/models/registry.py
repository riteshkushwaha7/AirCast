import argparse
import json
from datetime import UTC, datetime
from pathlib import Path


def register_model(registry_dir: Path, metadata: dict) -> Path:
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%SZ")
    model_dir = registry_dir / f"{metadata['model_name']}_{timestamp}"
    model_dir.mkdir(parents=True, exist_ok=True)

    meta_path = model_dir / "metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    latest_link = registry_dir / "latest"
    latest_pointer = registry_dir / "latest.txt"
    if latest_link.exists() or latest_link.is_symlink():
        latest_link.unlink()

    try:
        latest_link.symlink_to(model_dir.name, target_is_directory=True)
    except OSError:
        # Windows environments without symlink permission fall back to a pointer file.
        latest_pointer.write_text(model_dir.name, encoding="utf-8")

    return model_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default="models/registry")
    parser.add_argument("--model-name", default="aqi_lstm")
    parser.add_argument("--metrics", default='{"mae": 18.2}')
    args = parser.parse_args()

    registry_dir = Path(args.registry)
    registry_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "model_name": args.model_name,
        "registered_at": datetime.now(tz=UTC).isoformat(),
        "metrics": json.loads(args.metrics),
    }
    model_dir = register_model(registry_dir, metadata)
    print(f"Registered model at {model_dir}")


if __name__ == "__main__":
    main()
