package com.evolog;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Assertions;

import java.io.*;
import java.util.*;
import java.lang.ProcessBuilder.Redirect;

import org.evomaster.core.search.TargetInfo;

public class EvoMasterMockTest {
    private final String evotest = "src/main/resources/evotest.py";
    private final String testLogFilePath = "logs/test-log";
    private final LogCollector plugin = new LogCollector();

    @BeforeEach
    void callStartCollect() {
        plugin.goingToStartExecutingNewTest();
    }

    private void runTest(String testId) {
        ProcessBuilder pb = new ProcessBuilder("python3", evotest, testId);
        pb.redirectErrorStream(true);
        pb.redirectOutput(Redirect.appendTo(new File(testLogFilePath)));

        try {
            Process process = pb.start();
            int exitCode = process.waitFor();
            Assertions.assertEquals(0, exitCode,
                    "Running an EvoMaster test with Python failed, exit code: " + exitCode);

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            Assertions.fail("Python execution threw an exception: " + e.getMessage());
        }
    }

    private List<TargetInfo> finishCollecting() {
        List<TargetInfo> targets = plugin.testFinishedCollectResult();
        Assertions.assertNotNull(targets, "Method returned null instead of a list");

        return targets;
    }

    @Test
    void runMockLoop() {
        for (int i = 2; i < 10; i++) {
            runTest(String.valueOf(i));
            List<TargetInfo> targets = finishCollecting();

            for (TargetInfo t : targets) {
                Assertions.assertNotNull(t.getDescriptiveId(), "Target descriptiveId should not be null");
                System.out.println("DescriptiveId: " + t.getDescriptiveId());
            }
        }
    }
}