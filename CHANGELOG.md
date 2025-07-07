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

[Unreleased]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.2-beta...HEAD
[0.2.2-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.1-beta...v0.2.2-beta
[0.2.1-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.2.0-beta...v0.2.1-beta
[0.2.0-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/compare/v0.1.0-beta...v0.2.0-beta
[0.1.0-beta]: https://github.com/PaulMRamirez/yamcs-mcp-server/releases/tag/v0.1.0-beta