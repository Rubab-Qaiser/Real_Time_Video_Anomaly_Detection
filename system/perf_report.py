"""Simple perf report tool for DashboardClient CSV logs.

Usage:
    python perf_report.py --log system/perf_log.csv

Produces a small summary (counts, avg/median queue delay, post duration,
request elapsed, error rate, percentiles).
"""
import argparse
import csv
import statistics
from typing import List


def to_float(v):
    try:
        return float(v)
    except Exception:
        return None


def summarize(values: List[float]):
    values = [v for v in values if v is not None]
    if not values:
        return None
    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        "p90": sorted(values)[int(len(values) * 0.9) - 1],
        "p95": sorted(values)[int(len(values) * 0.95) - 1] if len(values) >= 20 else sorted(values)[-1],
    }


def print_summary(title, stats):
    if stats is None:
        print(f"{title}: no data")
        return
    print(f"{title}: count={stats['count']} mean={stats['mean']:.3f}s median={stats['median']:.3f}s p90={stats['p90']:.3f}s p95={stats['p95']:.3f}s stdev={stats['stdev']:.3f}s")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--log", required=True, help="Path to perf CSV (perf_log.csv)")
    args = p.parse_args()

    queue_delays = []
    post_durations = []
    request_elapsed = []
    http_statuses = []
    errors = 0
    total = 0

    with open(args.log, newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            total += 1
            enqueue = to_float(row.get('enqueue_ts'))
            post_start = to_float(row.get('post_start_ts'))
            post_end = to_float(row.get('post_end_ts'))
            req_elapsed = to_float(row.get('request_elapsed_s'))
            status = row.get('http_status')
            err = row.get('error')

            if enqueue and post_start:
                queue_delays.append(post_start - enqueue)
            if post_start and post_end:
                post_durations.append(post_end - post_start)
            if req_elapsed:
                request_elapsed.append(req_elapsed)
            if status:
                http_statuses.append(status)
            if err and err.strip():
                errors += 1

    print(f"Perf log: {args.log}")
    print(f"Total rows: {total}  errors: {errors}  error_rate={(errors/total*100) if total else 0:.2f}%")

    print_summary("Queue delay (enqueue->post_start)", summarize(queue_delays))
    print_summary("Post duration (post_end - post_start)", summarize(post_durations))
    print_summary("Request elapsed (requests.elapsed)", summarize(request_elapsed))

    # HTTP status distribution
    status_counts = {}
    for s in http_statuses:
        status_counts[s] = status_counts.get(s, 0) + 1
    if status_counts:
        print("HTTP status distribution:")
        for s, c in sorted(status_counts.items()):
            print(f"  {s}: {c}")


if __name__ == '__main__':
    main()
