# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- N/A

### Fixed
- N/A

## [0.3.1-beta] - 2025-08-04

### Changed
- Improved documentation to avoid prescriptive language about tool usage
- Updated sample prompts to focus on outcomes rather than implementation details
- Clarified that the AI/LLM determines which tools to use based on context

### Fixed
- Documentation now properly sets user expectations about how MCP works
- Removed misleading "The AI will use X tool" statements throughout docs

## [0.3.0-beta] - 2025-08-04

### Added
- Commands server for executing and managing spacecraft commands
  - `commands/list_commands` - List available commands for execution
  - `commands/describe_command` - Get detailed command information including arguments
  - `commands/run_command` - Execute commands with full argument support
  - `commands/read_log` - Read command execution history from archive
- Robust handling of command arguments as both JSON objects and JSON strings
  - Automatically parses JSON strings to objects for compatibility with Claude Desktop
  - Addresses known issue where some MCP clients send args as strings instead of objects

### Changed
- Improved `run_command` to accept both `dict[str, Any]` and string arguments
- Updated documentation to reflect that both argument formats are supported
- Enhanced test coverage for command argument validation

### Fixed
- Command execution errors when Claude Desktop sends arguments as JSON strings
- Input validation errors with message `'{"voltage_num": 1}' is not valid under any of the given schemas`

## [0.2.3-beta] - 2025-07-07

### Fixed
- Mypy type checking errors that were preventing CI/CD pipeline completion
- Added targeted type ignore comments for unfollowed imports from yamcs library
- Added type ignore for FastMCP generic type parameter
- Added type ignore for untyped decorators from mcp.tool()

### Changed
- Removed unnecessary mypy configuration changes
- Maintained strict type checking while accommodating external library limitations

## [0.2.2-beta] - 2025-07-07

### Fixed
- All linting errors (E501 line too long)
- Code formatting to pass CI/CD checks

### Changed
- Minor code refactoring for better readability

## [0.2.1-beta] - 2025-07-07

### Fixed
- Updated all USERNAME placeholders to PaulMRamirez in documentation
- Changed documentation URL to point to GitHub README until Pages is set up

## [0.2.0-beta] - 2025-07-07

### Added
- Alarms server for comprehensive alarm monitoring and management
- Summary statistics in `list_alarms` (total, acknowledged, unacknowledged, shelved, ok, latched)
- `describe_alarm` tool for detailed alarm information
- Alarm acknowledgment, shelving, and clearing capabilities
- Alarm history reading from archive
- `alarms://list` resource showing active alarms summary

### Changed
- **BREAKING**: Refactored from component-based to server-based architecture
- **BREAKING**: Renamed all `get_*` tools to `describe_*` for consistency
- **BREAKING**: Renamed classes to plural forms (LinksServer, ProcessorsServer, InstancesServer)
- **BREAKING**: Updated environment variables (removed `YAMCS_MCP_` prefix)
- Moved base_server.py from components/ to servers/ directory
- Removed unused archive.py functionality
- Removed `_register_common_tools` from base server
- Updated all tool names for consistency (e.g., `get_processor` → `describe_processor`)
- Replaced `control_processor` with `delete_processor`
- Updated processor resources (removed `processors://status`, added `processors://list`)
- Comprehensive documentation updates to reflect new architecture

### Fixed
- Link data reporting (use correct attribute names from Yamcs API)
- Alarm field names to match Yamcs Python client API
- Various API inconsistencies with actual Yamcs responses

### Removed
- Archive server and all archive-related functionality
- Component registration pattern in favor of server mounting
- Various redundant tools and resources

## [0.1.0-beta] - 2025-01-01

### Added
- Initial project setup with FastMCP 2.x
- Mission Database (MDB) server with parameter and command access
- TM/TC Processing server for real-time operations
- Link Management server for data link control
- Object Storage server for bucket and object management
- Instance Management server for Yamcs instance control
- Comprehensive test suite
- Documentation and examples
- Development tooling (ruff, mypy, pre-commit)

[Unreleased]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.3-beta...HEAD
[0.2.3-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.2-beta...v0.2.3-beta
[0.2.2-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.1-beta...v0.2.2-beta
[0.2.1-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.0-beta...v0.2.1-beta
[0.2.0-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.1.0-beta...v0.2.0-beta
[0.1.0-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/releases/tag/v0.1.0-beta