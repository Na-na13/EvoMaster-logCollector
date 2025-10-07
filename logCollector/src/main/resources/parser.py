import datetime
import docker
import polars as pl
import os
import sys

from loglead.enhancers import EventLogEnhancer
from loglead.loaders import RawLoader

def get_logs(start_time):
    # Local solution!! SUT and the plugin run on same machine
    # Still not clear, how to get the starting and ending times of test executions
    # to be able to get only the subset of logs
    # Start time can be passed from Java Process, is end time needed?
    client = docker.from_env()

    # Directory to store logs
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    output_dir = f"logs/evomaster-logs/v2-{timestamp}/"
    os.makedirs(output_dir, exist_ok=True)

    for container in client.containers.list():
        container_name = container.name
        log_file_path = os.path.join(output_dir, f"{container_name}.log")

        print(f"Fetching logs for container: {container_name}")

        # Get all logs since start_time
        raw_logs = container.logs(timestamps=True, since=int(start_time))
        log_lines = [line.decode("utf-8").strip() for line in raw_logs.splitlines()]

        # Write logs to file
        with open(log_file_path, "w", encoding="utf-8") as f:
            for line in log_lines:
                f.write(line + "\n")

        print(f"Logs for container {container_name} written to {log_file_path}")
    
    return output_dir


def unique_log_templates(start_time):
    # Retrieve the logs
    log_dir = get_logs(start_time)

    templates = []
    all_services = ["client", "code", "key", "refresh-token", "service", "token", "user"]
    
    for service in all_services:
        log_file_path = os.path.abspath(os.path.join(log_dir, f"light-oauth2-repl_v100-oauth2-{service}-1.log"))
        if not os.path.exists(log_file_path):
            print(f"Warning: log file {log_file_path} does not exist")
            continue

        # Do data loading
        print(f"Processing service: {service}")
        loader = RawLoader(
            filename=log_file_path
        )
        
        df = loader.execute()
        df = df.filter(pl.col("m_message").is_not_null())
        
        # Do data enhancing
        enhancer = EventLogEnhancer(df)
        enhancer.normalize(to_lower=True)
        df = enhancer.parse_drain(templates=True, persistence=True)

        templates_per_id = df.group_by("e_event_drain_id").agg(pl.col("e_event_drain_template"))
        templates_per_id_dict = templates_per_id.to_dict(as_series=False)
        template_id_mapping = dict(zip(templates_per_id_dict["e_event_drain_id"], templates_per_id_dict["e_event_drain_template"]))

        new_dict = {}
        for event_id, event_templates in template_id_mapping.items():
            if len(event_templates) == 1:
                new_dict[event_id] = event_templates[0]
                continue
            best_template = max(event_templates, key=lambda t: t.count("*"))
            new_dict[event_id] = best_template

        template_id_mapping_df = pl.DataFrame({"e_event_drain_id": list(new_dict.keys()), "e_event_drain_template": list(new_dict.values())})

        unique_templates = template_id_mapping_df["e_event_drain_template"].unique().to_list()
        templates.extend(unique_templates)

    return set(templates)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <start_time>")
        sys.exit(1)
    start_time = sys.argv[1]
    output_file = "templates/unique-templates.txt"
    result = unique_log_templates(start_time)
    with open(output_file, "w", encoding="utf-8") as out_file:
        for template in result:
            out_file.write(template + "\n")
