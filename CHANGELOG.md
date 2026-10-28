# Changelog

All notable changes to the MTN Cloud Python SDK are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

This changelog covers published releases from 0.3.1 onward. See the
[PyPI release history](https://pypi.org/project/mtn-cloud/#history) for older versions.

## [Unreleased]

## [0.4.1] - 2026-10-28

### Added

- Python 3.14 and 3.15 support, with both versions included in CI on Linux,
  macOS, and Windows.
- This changelog for tracking user-facing changes between releases.

## [0.4.0] - 2026-10-28

### Added

- `cloud.routers` for listing and inspecting routers, creating and deleting MTN
  routers, and waiting for provisioning or deletion to finish.
- Typed router models and creation inputs for groups, clouds, resource pools,
  public networks, and internal subnets. The MTN router type is selected
  automatically.
- Router IDs in post-create read errors, provisioning failure errors, and polling
  timeouts so callers can inspect or clean up affected routers.
- A router example and networking guide that discover existing network and subnet
  IDs instead of hardcoding them.

### Fixed

- Network lookup by name now checks exact matches across pages and raises
  `ValueError` for ambiguous names instead of silently choosing the first match.

## [0.3.4] - 2026-10-08

### Changed

- Added an MTN Cloud pricing link to the README and corrected a configuration
  module docstring. No runtime behavior changes.

## [0.3.3] - 2026-08-28

### Changed

- Tokens and passwords are stored as masked `SecretStr` values. Use
  `config.get_token_value()` and `config.get_password_value()` when raw credentials
  are explicitly needed.
- Custom user agents preserve the SDK identity required by the MTN API edge.

### Fixed

- Secrets are redacted from debug logs and API error response payloads.
- Automatic status retries are limited to `GET`, `HEAD`, and `OPTIONS`, avoiding
  replay of mutating requests. Retry handling supports numeric and HTTP-date
  `Retry-After` values.
- Client configuration respects environment settings for TLS verification when
  `verify_ssl` is omitted.

## [0.3.2] - 2026-06-27

### Added

- `cloud.instances.provision()` for creating instances using group, instance-type,
  plan, and resource-pool names, with optional readiness waiting and dry-run output.
- A `py.typed` marker so type checkers can use the SDK's inline annotations.
- Provisioning recipes and a simplified instance-creation example.

## [0.3.1] - 2026-06-27

### Added

- `resource_pool_id` on network creation to place OpenStack networks in the
  selected resource pool.

### Fixed

- API responses containing `null` labels are normalized to empty lists.
- Network-type discovery requests up to 500 entries so OpenStack types beyond
  the default first page can be found.

[Unreleased]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.4.0...HEAD
[0.4.1]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.4.0...0.4.1
[0.4.0]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.3.4...v0.4.0
[0.3.4]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.3.3...v0.3.4
[0.3.3]: https://github.com/mahveotm/mtn-cloud-python/compare/77459ec702ab8f7990376fc383447a0a4407c8ec...v0.3.3
[0.3.2]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.3.1...77459ec702ab8f7990376fc383447a0a4407c8ec
[0.3.1]: https://github.com/mahveotm/mtn-cloud-python/compare/v0.3.0...v0.3.1
