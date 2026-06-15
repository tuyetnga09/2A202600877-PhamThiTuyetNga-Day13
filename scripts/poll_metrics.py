from __future__ import annotations

import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
OUT_PATH = Path("data/metrics_timeseries.csv")

# Columns flattened from /metrics snapshot() for easy charting in
# Grafana / Google Sheets / Excel. error_breakdown is summed to a single count.
FIELDS = [
    "ts",
    "traffic",
    "latency_p50",
    "latency_p95",
    "latency_p99",
    "avg_cost_usd",
    "total_cost_usd",
    "tokens_in_total",
    "tokens_out_total",
    "error_count",
    "quality_avg",
]


def flatten(snapshot: dict) -> dict:
    row = {k: snapshot.get(k) for k in FIELDS if k in snapshot}
    row["ts"] = datetime.now(timezone.utc).isoformat()
    row["error_count"] = sum(snapshot.get("error_breakdown", {}).values())
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll /metrics and append to a CSV time series.")
    parser.add_argument("--interval", type=float, default=15.0, help="Seconds between samples")
    parser.add_argument("--count", type=int, default=0, help="Number of samples (0 = run forever)")
    args = parser.parse_args()

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    new_file = not OUT_PATH.exists()

    with OUT_PATH.open("a", newline="", encoding="utf-8") as f, httpx.Client(timeout=10.0) as client:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()

        samples = 0
        while args.count == 0 or samples < args.count:
            try:
                snap = client.get(f"{BASE_URL}/metrics").json()
                row = flatten(snap)
                writer.writerow(row)
                f.flush()
                print(
                    f"{row['ts']} | traffic={row['traffic']} "
                    f"p95={row['latency_p95']}ms cost=${row['total_cost_usd']} "
                    f"errors={row['error_count']} quality={row['quality_avg']}"
                )
            except Exception as exc:  # pragma: no cover
                print(f"Error polling /metrics: {exc}")

            samples += 1
            if args.count == 0 or samples < args.count:
                time.sleep(args.interval)

    print(f"Wrote {samples} samples to {OUT_PATH}")


if __name__ == "__main__":
    main()
