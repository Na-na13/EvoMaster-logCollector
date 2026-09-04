import datetime
import docker
import polars as pl
import os
import sys

from loglead.enhancers import EventLogEnhancer
from loglead.loaders import RawLoader

# If set, only containers belonging to this Docker Compose project are collected.
# Set via the LOG_COLLECTOR_PROJECT environment variable before starting EvoMaster.
COMPOSE_PROJECT = os.environ.get("COMPOSE_PROJECT")

def get_logs(start_time_ms, end_time_ms):
    client = docker.from_env()

    # Convert millisecond timestamps to datetime for the Docker SDK.
    # The SDK rejects floats; datetime preserves sub-second precision.
    since = datetime.datetime.utcfromtimestamp(int(start_time_ms) / 1000.0)
    until = datetime.datetime.utcfromtimestamp(int(end_time_ms) / 1000.0)

    # Directory to store logs
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = f"logs/evomaster-logs/v2-{timestamp}/"
    os.makedirs(output_dir, exist_ok=True)

    filters = {"label": f"com.docker.compose.project={COMPOSE_PROJECT}"} if COMPOSE_PROJECT else {}
    containers = client.containers.list(filters=filters)

    if COMPOSE_PROJECT:
        print(f"Collecting logs for Compose project: {COMPOSE_PROJECT}", file=sys.stderr)
    else:
        print("COMPOSE_PROJECT not set — collecting logs from all running containers", file=sys.stderr)

    container_names = []
    for container in containers:
        container_name = container.name
        container_names.append(container_name)
        log_file_path = os.path.join(output_dir, f"{container_name}.log")

        print(f"Fetching logs for container: {container_name}", file=sys.stderr)

        raw_logs = container.logs(timestamps=True, since=since, until=until)
        log_lines = [line.decode("utf-8", errors="replace").strip() for line in raw_logs.splitlines()]

        with open(log_file_path, "w", encoding="utf-8") as f:
            for line in log_lines:
                f.write(line + "\n")

        print(f"Logs for container {container_name} written to {log_file_path}", file=sys.stderr)

    return output_dir, container_names


def unique_log_templates(start_time_ms, end_time_ms):
    log_dir, container_names = get_logs(start_time_ms, end_time_ms)

    templates = []
    for container_name in container_names:
        log_file_path = os.path.abspath(os.path.join(log_dir, f"{container_name}.log"))
        if not os.path.exists(log_file_path):
            print(f"Warning: log file {log_file_path} does not exist", file=sys.stderr)
            continue

        print(f"Processing container: {container_name}", file=sys.stderr)
        loader = RawLoader(filename=log_file_path)

        df = loader.execute()
        df = df.filter(pl.col("m_message").is_not_null())
        if df.is_empty():
            print(f"No log messages for {container_name} in this time window — skipping", file=sys.stderr)
            continue

        # Strip the log header (docker timestamp, app timestamp, thread name,
        # correlation ID, log level) so Drain clusters on the logger class +
        # message content only. Non-matching lines are left unchanged.
        df = df.with_columns(
            pl.col("m_message").str.replace(
                r"(?i)^.*?\s+(?:DEBUG|INFO|WARN|ERROR)\s+", ""
            )
        )

        # Do data enhancing
        enhancer = EventLogEnhancer(df)
        enhancer.normalize(to_lower=True)
        df = enhancer.parse_drain(templates=True, persistence=True)

        # Use Drain cluster ID as the stable identifier and keep the template text
        # alongside it for debugging. The ID never changes once a cluster is created,
        # even as Drain refines the template text over subsequent runs.
        for row in df.select(["e_event_drain_id", "e_event_drain_template"]).unique().to_dicts():
            drain_id = row["e_event_drain_id"]
            template = row["e_event_drain_template"]
            templates.append(f"{container_name}:{drain_id}\t{template}")

    return set(templates)

def daemon_loop():
    output_file = "templates/unique-templates.txt"
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            print(f"ERROR: invalid request: {line}", flush=True)
            continue
        start_time_ms, end_time_ms = parts
        try:
            result = unique_log_templates(start_time_ms, end_time_ms)
            with open(output_file, "w", encoding="utf-8") as f:
                for template in sorted(result):
                    f.write(template + "\n")
            print("OK", flush=True)
        except Exception as e:
            error_msg = str(e).replace("\n", " ").replace("\r", " ")
            print(f"ERROR: {error_msg}", flush=True)

if __name__ == "__main__":
    daemon_loop()
