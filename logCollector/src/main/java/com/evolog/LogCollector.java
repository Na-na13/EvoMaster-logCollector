package com.evolog;

import java.io.*;
import java.lang.ProcessBuilder.Redirect;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

import org.evomaster.core.search.AdditionalTargetCollector;
import org.evomaster.core.search.TargetInfo;
import org.evomaster.core.logging.LoggingUtil;
import org.slf4j.Logger;

public class LogCollector implements AdditionalTargetCollector {
    private final List<TargetInfo> results = new ArrayList<>();
    private final String pythonParser = "src/main/resources/parser.py";
    private final String logFilePath = "logs/processbuilder-log";
    private final String uniqueTemplatesFile = "templates/unique-templates.txt";
    private static final Logger log = LoggingUtil.Companion.getInfoLogger();

    private long startTimeEpoch;

    @Override
    public void goingToStartExecutingNewTest() {
        /*
         * Fresh start for test evaulation.
         * Get the starting timestamp for the Python process.
         */
        log.info("Going to start executing new tests");
        results.clear();
        startTimeEpoch = Instant.now().getEpochSecond();

    }

    @Override
    public void reportActionIndex(int actionIndex) {
        // always keep actionIndex = -1
    }

    @Override
    public List<TargetInfo> testFinishedCollectResult() {
        /*
         * Retrieve the unique log templatess from the shared location
         * for each template, create a TargetInfo class instance
         * e.g. results.add(new TargetInfo("target-1", 1));
         * Make an array/list out of those TargetInfo objects and pass it to EvoMaster
         * e.g. return results;
         */
        log.info("Test finished, collect results");

        ProcessBuilder pb = new ProcessBuilder("python3", pythonParser, String.valueOf(startTimeEpoch));
        pb.redirectErrorStream(true);
        pb.redirectOutput(Redirect.appendTo(new File(logFilePath)));

        try {
            Process process = pb.start();
            int exitCode = process.waitFor();
            if (exitCode != 0) {
                System.err.println("Python (parser) failed, exit code: " + exitCode);
                return null;
            }

            Path resultPath = Paths.get(uniqueTemplatesFile);
            if (!Files.exists(resultPath)) {
                System.err.println("Result file not found: " + uniqueTemplatesFile);
                return null;
            }

            Files.readAllLines(resultPath, StandardCharsets.UTF_8)
                    .forEach(line -> {
                        String template = line.trim();
                        if (!template.isEmpty()) {
                            results.add(new TargetInfo(template, 1.0, -1));
                        }
                    });

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            throw new RuntimeException("Python failed in parsing of log templates", e);
        }

        return results;
    }
}
