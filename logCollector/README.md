# EvoMaster LogCollector Plugin

An EvoMaster plugin that collects Docker container logs during fuzzing and converts them into additional coverage targets using [LogLead](https://github.com/EvoTestOps/LogLead) Drain log parsing.

Each unique log template observed during a test is reported to EvoMaster as a `TargetInfo`, letting the search engine prefer test cases that trigger new log patterns.

## Prerequisites

- Java 11+
- Python 3.10+
- Docker (SUT must be running as Docker containers on the same host)
- Python dependencies (install into a virtual environment):

```bash
pip install -r requirements.txt
pip install git+https://github.com/EvoTestOps/LogLead.git@main
```

## Build

```bash
mvn clean package -DskipTests
```

The plugin JAR bundles `parser.py` internally — no extra files need to be distributed alongside it.

## Usage

Place `evomaster.jar` and the plugin JAR in the same directory, then add the plugin JAR to the classpath. EvoMaster discovers the plugin automatically via `ServiceLoader`.

```bash
java -cp evomaster.jar:logCollector-*.jar \
     org.evomaster.core.Main \
     --blackBox true \
     --bbSwaggerUrl "<swagger-url>" \
     --bbTargetUrl "http://localhost:<port>" \
     --maxTime 60s
```

A convenience script for running multiple light-oauth2 microservices is provided in [run_evomaster.sh](run_evomaster.sh).

## Container filtering (recommended)

By default the plugin collects logs from **all** running containers. To restrict collection to a specific Docker Compose project, set `LOG_COLLECTOR_PROJECT` before starting EvoMaster:

```bash
export LOG_COLLECTOR_PROJECT=my-compose-project
java -cp evomaster.jar:logCollector-*.jar org.evomaster.core.Main ...
```

The value must match the Docker Compose project name (the `com.docker.compose.project` label applied automatically by `docker compose up`). This is usually the directory name of the `docker-compose.yml` file.

## How it works

1. At startup the plugin extracts `parser.py` from the JAR and starts it as a persistent background daemon.
2. Before each test EvoMaster calls `goingToStartExecutingNewTest()` — the plugin records the start timestamp.
3. After each test EvoMaster calls `testFinishedCollectResult()` — the plugin sends the time window to the daemon.
4. The daemon fetches container logs for that window via the Docker API, runs Drain clustering via LogLead, and writes unique templates to `templates/unique-templates.txt`.
5. The plugin reads the template file and returns one `TargetInfo` per unique template to EvoMaster.

## Output

| Path | Contents |
|---|---|
| `templates/unique-templates.txt` | All unique log templates seen across the run |
| `logs/processbuilder-log` | Daemon stderr (Docker API calls, warnings) |
| `logs/evomaster-logs/` | Per-test raw container log files (deleted on shutdown) |

## Limitations (MVP)

- SUT must run on the same machine as EvoMaster (Docker socket access required).
- Container filtering requires the SUT to be started with Docker Compose (for automatic project labels).
- `actionIndex` is always `-1` — log targets are not attributed to individual HTTP actions.
