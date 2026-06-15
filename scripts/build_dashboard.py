"""Render a 6-panel observability dashboard PNG from data/metrics_timeseries.csv.

Usage:
    python scripts/poll_metrics.py --interval 2 --count 30   # collect samples first
    python scripts/build_dashboard.py                        # -> docs/img/dashboard.png

Panels (per docs/dashboard-spec.md):
  1. Latency P50/P95/P99   2. Traffic   3. Error rate
  4. Cost over time        5. Tokens in/out   6. Quality proxy
Threshold/SLO lines come from config/slo.yaml objectives.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV_PATH = Path("data/metrics_timeseries.csv")
OUT_PATH = Path("docs/img/dashboard.png")

# SLO thresholds (keep in sync with config/slo.yaml)
SLO_LATENCY_P95_MS = 3000
SLO_ERROR_RATE_PCT = 2.0
SLO_QUALITY_AVG = 0.75


def load_rows() -> list[dict]:
    if not CSV_PATH.exists():
        raise SystemExit(f"{CSV_PATH} not found. Run scripts/poll_metrics.py first.")
    with CSV_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("No samples in CSV. Run poll_metrics.py while sending load.")
    return rows


def col(rows: list[dict], key: str) -> list[float]:
    out = []
    for r in rows:
        try:
            out.append(float(r.get(key) or 0))
        except ValueError:
            out.append(0.0)
    return out


def main() -> None:
    rows = load_rows()
    x = list(range(1, len(rows) + 1))  # sample index

    traffic = col(rows, "traffic")
    errors = col(rows, "error_count")
    error_rate = [
        100 * e / (t + e) if (t + e) else 0.0 for t, e in zip(traffic, errors)
    ]

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(16, 9))
    fig.suptitle("Day 13 Observability Dashboard - Phạm Thị Tuyết Nga (2A202600877)", fontsize=14)

    # 1. Latency
    ax = axes[0][0]
    ax.plot(x, col(rows, "latency_p50"), label="p50")
    ax.plot(x, col(rows, "latency_p95"), label="p95")
    ax.plot(x, col(rows, "latency_p99"), label="p99")
    ax.axhline(SLO_LATENCY_P95_MS, color="red", ls="--", lw=1, label=f"SLO {SLO_LATENCY_P95_MS}ms")
    ax.set_title("1. Latency (ms)")
    ax.set_xlabel("sample")
    ax.set_ylabel("ms")
    ax.legend(fontsize=8)

    # 2. Traffic
    ax = axes[0][1]
    ax.plot(x, traffic, color="tab:blue")
    ax.set_title("2. Traffic (cumulative requests)")
    ax.set_xlabel("sample")
    ax.set_ylabel("requests")

    # 3. Error rate
    ax = axes[0][2]
    ax.plot(x, error_rate, color="tab:red")
    ax.axhline(SLO_ERROR_RATE_PCT, color="red", ls="--", lw=1, label=f"SLO {SLO_ERROR_RATE_PCT}%")
    ax.set_title("3. Error rate (%)")
    ax.set_xlabel("sample")
    ax.set_ylabel("%")
    ax.legend(fontsize=8)

    # 4. Cost
    ax = axes[1][0]
    ax.plot(x, col(rows, "total_cost_usd"), color="tab:green")
    ax.set_title("4. Cost over time (USD, cumulative)")
    ax.set_xlabel("sample")
    ax.set_ylabel("USD")

    # 5. Tokens in/out
    ax = axes[1][1]
    ax.plot(x, col(rows, "tokens_in_total"), label="tokens_in")
    ax.plot(x, col(rows, "tokens_out_total"), label="tokens_out")
    ax.set_title("5. Tokens in/out (cumulative)")
    ax.set_xlabel("sample")
    ax.set_ylabel("tokens")
    ax.legend(fontsize=8)

    # 6. Quality
    ax = axes[1][2]
    ax.plot(x, col(rows, "quality_avg"), color="tab:purple")
    ax.axhline(SLO_QUALITY_AVG, color="red", ls="--", lw=1, label=f"SLO {SLO_QUALITY_AVG}")
    ax.set_title("6. Quality proxy (avg)")
    ax.set_xlabel("sample")
    ax.set_ylabel("score")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(OUT_PATH, dpi=120)
    print(f"Saved dashboard with 6 panels -> {OUT_PATH} ({len(rows)} samples)")


if __name__ == "__main__":
    main()
