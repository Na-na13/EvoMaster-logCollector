# Development Notes

## Changes made after rebasing onto new upstream EvoMaster

### `core/src/main/kotlin/.../EnterpriseFitness.kt`
- Removed the old `ServiceLoader`-based plugin registry (`pluginRegistry`, `init` block, `ServiceLoader` import) — this was the wrong approach for the new EvoMaster
- Added import for `LogCollector`
- Implemented `@PostConstruct initialize()`: instantiates `LogCollector` when `config.enableLogCollector` is true, kept the existing TODO comment

### `core/src/main/kotlin/org/evomaster/core/EMConfig.kt`
- Added `@Experimental @Cfg(...) var enableLogCollector = false` flag at the end of the experimental properties section

### `core/pom.xml`
- Added `extra-log-collector` as a dependency alongside `extra-shared`

### `pom.xml` (root)
- Added `extra-log-collector` to `<dependencyManagement>` so its version is resolved centrally

### `core-extra/pom.xml`
- Registered `log-collector` as a new submodule

### `core-extra/log-collector/` (new module)
- `pom.xml` — parent `evomaster-core-extra`, depends on `extra-shared` and `slf4j-api`
- `LogCollector.java` — migrated from old `com.evolog` package to `org.evomaster.core.extra.logcollector`, updated imports to use `core-extra/shared` types, replaced `LoggingUtil` with `LoggerFactory`, added full JavaDoc (class description, field comments, side-effect documentation on constructors)
- `parser.py` — copied as-is from old module into `src/main/resources/`
- `LogCollectorTest.java` — migrated from old module to correct package, updated `TargetInfo` import
- Test resources — `replay_daemon.py` and 8 sample log files copied to `src/test/resources/`

### `logCollector/src/test/java/com/evolog/EvoMasterMockTest.java`
- Deleted — was an integration test with hardcoded paths, `System.out.println`, and tight coupling to the old module structure
