import argparse
import json
import sys
import urllib.error
import urllib.request


def get_json(url: str, timeout: float) -> tuple[bool, dict | None, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
        return True, json.loads(payload), None
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, None, str(exc)
    except json.JSONDecodeError:
        return False, None, "non-json response"


def is_reachable(url: str, timeout: float) -> tuple[bool, str | None]:
    try:
        with urllib.request.urlopen(url, timeout=timeout):
            return True, None
    except (urllib.error.URLError, TimeoutError) as exc:
        return False, str(exc)


def main() -> None:
    parser = argparse.ArgumentParser(description="Check AirWise local health endpoints")
    parser.add_argument("--api-url", default="http://localhost:8000/api/v1/admin/health")
    parser.add_argument("--web-url", default="http://localhost:3000")
    parser.add_argument("--timeout", type=float, default=3.0)
    args = parser.parse_args()

    api_ok, api_payload, api_error = get_json(args.api_url, args.timeout)
    web_ok, web_error = is_reachable(args.web_url, args.timeout)

    print("AirWise health check")
    print(f"- API endpoint: {args.api_url}")
    if api_ok and api_payload is not None:
        print(f"  status={api_payload.get('status')} postgres={api_payload.get('postgres')} influx={api_payload.get('influx')}")
    else:
        print(f"  status=unreachable error={api_error}")

    print(f"- Web endpoint: {args.web_url}")
    if web_ok:
        print("  status=reachable")
    else:
        print(f"  status=unreachable error={web_error}")

    if api_ok and web_ok:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()
