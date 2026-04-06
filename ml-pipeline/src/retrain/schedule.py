import argparse
import subprocess
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler


def run_training(config_path: str) -> None:
    command = ["python", "-m", "src.models.train_lstm", "--config", config_path]
    subprocess.run(command, check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--interval-hours", type=int, default=24)
    parser.add_argument("--oneshot", action="store_true")
    args = parser.parse_args()

    config_path = str(Path(args.config))

    if args.oneshot:
        run_training(config_path)
        return

    scheduler = BlockingScheduler()
    scheduler.add_job(run_training, "interval", hours=args.interval_hours, args=[config_path])
    print(f"Retraining scheduler active every {args.interval_hours} hours")
    scheduler.start()


if __name__ == "__main__":
    main()
