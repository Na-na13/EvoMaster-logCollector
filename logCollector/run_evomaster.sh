#!/bin/bash
# Runs EvoMaster in black-box mode with the logCollector plugin for each
# light-oauth2 microservice. The SUT (Docker containers) must already be running.
#
# Usage:
#   ./run_evomaster.sh              # run all services
#   ./run_evomaster.sh token        # run a single service by name
#
# Place this script, evomaster.jar, and logCollector-*.jar in the SUT root
# (next to docker-compose-oauth2-mysql.yml). No other files needed — parser.py
# is bundled inside the logCollector JAR and extracted automatically at startup.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVOMASTER_JAR="$SCRIPT_DIR/evomaster.jar"
PLUGIN_JAR="$SCRIPT_DIR/logCollector-4.0.1-SNAPSHOT.jar"

# --- Service definitions: name → port ---
declare -A SERVICE_PORT
SERVICE_PORT["client"]="6884"
SERVICE_PORT["code"]="6881"
SERVICE_PORT["key"]="6886"
SERVICE_PORT["refresh-token"]="6887"
SERVICE_PORT["service"]="6883"
SERVICE_PORT["token"]="6882"
SERVICE_PORT["user"]="6885"
# ----------------------------------------

run_service() {
  local service="$1"
  if [[ -z "${SERVICE_PORT[$service]}" ]]; then
    echo "ERROR: unknown service '$service'. Known: ${!SERVICE_PORT[*]}"
    exit 1
  fi

  local port="${SERVICE_PORT[$service]}"
  local target_url="http://localhost:${port}"
  local swagger_url="file://$(pwd)/db/mysql/config/oauth2-${service}/openapi.yaml"
  local output_dir="generated_evolog_tests_v3/${service}"

  echo "==> Running EvoMaster for service: $service (port $port)"
  echo "    Target URL : $target_url"
  echo "    Swagger URL: $swagger_url"
  echo "    Output dir : $output_dir"
  echo ""

  # The plugin JAR is added to the classpath alongside evomaster.jar.
  # ServiceLoader discovers LogCollector via META-INF/services at startup.
  java -cp "$EVOMASTER_JAR:$PLUGIN_JAR" \
       org.evomaster.core.Main \
       --blackBox true \
       --bbSwaggerUrl "$swagger_url" \
       --bbTargetUrl "$target_url" \
       --outputFolder "$output_dir" \
       --maxTime 30s \
       --ratePerMinute 60

  echo "==> Done: $service"
  echo ""
}

if [[ $# -eq 1 ]]; then
  run_service "$1"
else
  for service in "${!SERVICE_PORT[@]}"; do
    run_service "$service"
  done
fi
