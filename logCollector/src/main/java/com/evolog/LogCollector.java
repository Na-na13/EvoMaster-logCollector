package com.evolog;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

import org.evomaster.core.search.AdditionalTargetCollector;
import org.evomaster.core.search.TargetInfo;
import org.evomaster.core.logging.LoggingUtil;
import org.slf4j.Logger;

public class LogCollector implements AdditionalTargetCollector {
  private final List<TargetInfo> results = new ArrayList<>();
  private static final Logger log = LoggingUtil.Companion.getInfoLogger();

  // All file paths are resolved relative to the working directory (CWD) so the
  // plugin works regardless of where the JAR is placed. parser.py is extracted
  // from inside the JAR to a temp file at startup, so no file needs to be
  // distributed alongside the JAR.
  private final Path workDir;
  private String pythonParser;         // temp file path of the extracted parser.py
  private String[] daemonCommand;      // command used to start the daemon process
  private String logFilePath;          // daemon stderr log: {cwd}/logs/processbuilder-log
  private String uniqueTemplatesFile;  // results file: {cwd}/templates/unique-templates.txt
  private final String composeProject; // Docker Compose project to filter containers (LOG_COLLECTOR_PROJECT env var)

  private long startTimeMillis;

  // Persistent daemon: started once, reused for every test to avoid per-test
  // Python startup overhead (docker, polars, loglead imports).
  // Non-final so the daemon can be restarted if it crashes.
  private Process daemonProcess;
  private BufferedWriter daemonIn;
  private BufferedReader daemonOut;

  public LogCollector() {
    workDir = Paths.get("").toAbsolutePath();
    composeProject = System.getenv("LOG_COLLECTOR_PROJECT");

    // Extract parser.py from the JAR to a temp file so the plugin works when the
    // JAR is placed anywhere (e.g. the SUT root) without extra files alongside it.
    try {
      Path parserTemp = Files.createTempFile("evomaster-parser-", ".py");
      parserTemp.toFile().deleteOnExit();
      try (InputStream is = LogCollector.class.getResourceAsStream("/parser.py")) {
        if (is == null) throw new RuntimeException("parser.py not found inside the plugin JAR");
        Files.copy(is, parserTemp, StandardCopyOption.REPLACE_EXISTING);
      }
      pythonParser = parserTemp.toString();
    } catch (IOException e) {
      throw new RuntimeException("Failed to extract parser.py from JAR", e);
    }

    daemonCommand = new String[]{"python3", "-u", pythonParser};
    initCommon();
  }

  // For tests: skip JAR extraction and drive a custom daemon command instead.
  LogCollector(String[] daemonCommand) {
    workDir = Paths.get("").toAbsolutePath();
    this.daemonCommand = daemonCommand;
    composeProject = null;
    initCommon();
  }

  private void initCommon() {
    logFilePath         = workDir.resolve("logs/processbuilder-log").toString();
    uniqueTemplatesFile = workDir.resolve("templates/unique-templates.txt").toString();

    // Ensure the logs directory exists and truncate the parser log so it contains
    // only this run's output.
    try {
      Files.createDirectories(Paths.get(logFilePath).getParent());
      Files.newOutputStream(Paths.get(logFilePath),
          StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING).close();
    } catch (IOException ignored) {}

    // Ensure the templates directory exists (parser.py writes there).
    try {
      Files.createDirectories(Paths.get(uniqueTemplatesFile).getParent());
    } catch (IOException ignored) {}

    // Start the Python daemon. Heavy imports (docker, polars, loglead) are loaded here
    // and reused for every test. -u disables Python's output buffering so responses
    // reach Java immediately.
    try {
      startDaemon();
    } catch (IOException e) {
      throw new RuntimeException("Failed to start parser daemon", e);
    }

    Path evoLogsDir = workDir.resolve("logs/evomaster-logs");
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      // Closing daemonIn signals the Python daemon to exit cleanly (EOF on stdin).
      try { daemonIn.close(); } catch (IOException ignored) {}
      // Delete per-test Docker log files collected during this EvoMaster run.
      if (!Files.exists(evoLogsDir)) return;
      try {
        Files.walk(evoLogsDir)
            .sorted(Comparator.reverseOrder())
            .forEach(p -> { try { Files.delete(p); } catch (IOException ignored) {} });
      } catch (IOException ignored) {}
    }));
  }

  // Starts (or restarts) the Python parser daemon and wires up its stdin/stdout streams.
  // The daemon runs with CWD as its working directory so relative paths in parser.py
  // (logs/, templates/) resolve to the same place as in Java.
  private void startDaemon() throws IOException {
    ProcessBuilder pb = new ProcessBuilder(daemonCommand);
    pb.directory(workDir.toFile());
    if (composeProject != null && !composeProject.isEmpty()) {
      pb.environment().put("COMPOSE_PROJECT", composeProject);
    }
    // Redirect daemon stderr to the parser log file so debug output does not
    // pollute the IPC stdout channel.
    pb.redirectError(new File(logFilePath));
    daemonProcess = pb.start();
    daemonIn  = new BufferedWriter(new OutputStreamWriter(
        daemonProcess.getOutputStream(), StandardCharsets.UTF_8));
    daemonOut = new BufferedReader(new InputStreamReader(
        daemonProcess.getInputStream(), StandardCharsets.UTF_8));
  }

  // Forcibly kills the current daemon and starts a fresh one so that subsequent
  // tests are not permanently blocked after a crash.
  private void restartDaemon() {
    try {
      daemonProcess.destroyForcibly();
    } catch (Exception ignored) {}
    try {
      startDaemon();
      System.err.println("Parser daemon restarted successfully");
    } catch (IOException e) {
      System.err.println("Failed to restart parser daemon: " + e.getMessage());
    }
  }

  @Override
  public void goingToStartExecutingNewTest() {
    log.info("Going to start executing new tests");
    results.clear();
    startTimeMillis = Instant.now().toEpochMilli();
  }

  @Override
  public void reportActionIndex(int actionIndex) {
    // always keep actionIndex = -1
  }

  @Override
  public List<TargetInfo> testFinishedCollectResult() {
    log.info("Test finished, collect results");
    results.clear();

    long endTimeMillis = Instant.now().toEpochMilli();

    // Guard: if the daemon crashed before we even send the request, restart it
    // now so the next test can use it, and skip this one (the time window is gone).
    if (!daemonProcess.isAlive()) {
      System.err.println("Parser daemon is not running — restarting for next test");
      restartDaemon();
      return Collections.emptyList();
    }

    try {
      // Send the test's time window to the daemon as "startMs endMs\n".
      daemonIn.write(startTimeMillis + " " + endTimeMillis);
      daemonIn.newLine();
      daemonIn.flush();

      // Poll for the daemon's response with a timeout so a hanging daemon
      // (e.g. Docker API stall, loglead deadlock) does not freeze EvoMaster.
      long deadline = System.currentTimeMillis() + 60_000;
      while (!daemonOut.ready()) {
        if (System.currentTimeMillis() > deadline) {
          System.err.println("Parser daemon timed out after 60 s — skipping this test");
          return Collections.emptyList();
        }
        if (!daemonProcess.isAlive()) {
          // Daemon died while processing; restart it so the next test works.
          System.err.println("Parser daemon exited unexpectedly — restarting for next test");
          restartDaemon();
          return Collections.emptyList();
        }
        try {
          Thread.sleep(100);
        } catch (InterruptedException ie) {
          Thread.currentThread().interrupt();
          return Collections.emptyList();
        }
      }

      // The daemon responds with "OK" on success or "ERROR: <message>" on failure.
      String response = daemonOut.readLine();
      if (response == null || !response.equals("OK")) {
        System.err.println("Parser daemon error: " + response);
        return Collections.emptyList();
      }

      Path resultPath = Paths.get(uniqueTemplatesFile);
      if (!Files.exists(resultPath)) {
        System.err.println("Result file not found: " + uniqueTemplatesFile);
        return Collections.emptyList();
      }

      // Each line is "{service}:{drain_id}\t{template_text}".
      // Only the stable drain ID is used as descriptiveId; the template text
      // is kept in the file for debugging but ignored here.
      for (String line : Files.readAllLines(resultPath, StandardCharsets.UTF_8)) {
        if (line.trim().isEmpty()) continue;
        String descriptiveId = "log:" + line.split("\t", 2)[0];
        results.add(new TargetInfo(descriptiveId, 1.0, -1));
      }

    } catch (IOException e) {
      e.printStackTrace();
      throw new RuntimeException("Parser daemon communication failed", e);
    }

    return results;
  }
}
