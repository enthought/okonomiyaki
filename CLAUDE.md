# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Okonomiyaki is Enthought's library for parsing and producing metadata for Enthought-specific
package formats: Enthought eggs (EDM/enpkg-compatible), version strings, platform strings, and
runtime archives. It underlies tooling like `edm`, `enpkg`, and `hatcher`. Python >= 3.6 (also
runs on 2.7-era code paths in places — check before assuming f-strings/walrus etc. are safe).

Install extras are split by concern:
- `pip install okonomiyaki` — version parsing only, no extra deps
- `pip install okonomiyaki[platforms]` — adds platform parsing (needs `attrs`, `distro`)
- `pip install okonomiyaki[formats]` — adds egg/archive tooling (needs `zipfile2`, `jsonschema`)
- `pip install okonomiyaki[all]` — everything
- `pip install okonomiyaki[test]` — test dependencies (`haas`, `distro`, `parameterized`, `testfixtures`, `packaging`)

Keep new code's dependencies within the extras structure above — don't add a hard dependency to
core `okonomiyaki` that belongs in `platforms` or `formats`.

## Commands

Install for development:
```
pip install -e .[all]
pip install -e .[test]
```

Run the test suite (uses `haas`, an Enthought unittest-style runner — not pytest):
```
# without optional dependencies (versions only)
python -m haas okonomiyaki.versions

# full suite, with all optional dependencies installed
python -m haas okonomiyaki
```

Run a single test module/class/method (dotted path, like `unittest`):
```
python -m haas okonomiyaki.versions.tests.test_enpkg_version
python -m haas okonomiyaki.versions.tests.test_enpkg_version.TestEnpkgVersion.test_some_case
```

Lint (flake8, max line length 120, `W503` ignored):
```
python -m flake8 okonomiyaki/
```

Coverage (as run in CI):
```
coverage run -p -m haas okonomiyaki
coverage combine
coverage report
```

CI (`.github/workflows/test.yml`) runs flake8 first (`code-lint` job), then the test matrix across
Python 3.8/3.11/3.12 on Linux/macOS/Windows, once without optional deps and once with `[all]`.

CLI entry point for inspecting eggs (`okonomiyaki/_cli/__init__.py`):
```
python -m okonomiyaki spec-depend <egg-path> [--metadata-version X.Y] [--sha256 ...]
python -m okonomiyaki pkg-info <egg-path>
python -m okonomiyaki summary <egg-path>
python -m okonomiyaki show-index <egg-path>
```

## Architecture

The package is organized into four largely independent subpackages, each importable on its own
with progressively more dependencies (`versions` has none; `platforms` needs `platforms` extra;
`file_formats`/`runtimes` need `formats` extra, which also pulls in `platforms`).

- **`okonomiyaki/versions/`** — version string parsing/comparison. Each scheme (`EnpkgVersion`,
  `PEP440Version`, `SemanticVersion`, `PEP386WorkaroundVersion`, `RuntimeVersion`,
  `MetadataVersion`) is its own immutable, hashable, totally-ordered value class with a
  `from_string` classmethod, following the same shape as `pep386.py`'s bundled PEP 386 parser.
  `EnpkgVersion` composes an upstream version (`PEP386WorkaroundVersion`) with an integer build
  number (`upstream-build` string form, e.g. `1.3.3-1`). These classes are designed to be usable
  as dict keys and are the vocabulary the rest of the codebase uses to represent versions —
  prefer reusing one of these over ad hoc string version handling.

- **`okonomiyaki/platforms/`** — platform/architecture representations, also frozen `attrs`
  value objects. `Arch`/`X86`/`X86_64`/`ARM64` (`_arch.py`) model CPU architecture; `Platform`
  (`_platform.py`) models OS/distribution (`OSKind`, `FamilyKind`, `NameKind` enums) plus arch;
  `EPDPlatform` (`epd_platform.py`) normalizes the various historical EPD/Canopy platform string
  spellings (`rh5-64`, `rh6_x86_64`, etc.) into one canonical representation — always parse
  through `EPDPlatform.from_string` rather than pattern-matching platform strings by hand.
  `pep425.py`/`_pep425_impl.py` compute PEP 425 (wheel) tags; `python_implementation.py` models
  Python implementation + ABI.

- **`okonomiyaki/file_formats/`** — the Enthought egg format. `_egg_info.py` (the largest module)
  implements `EggMetadata`, which reads/writes the `EGG-INFO/spec/depend` file inside an egg
  zip archive. This metadata is **explicitly versioned via `MetadataVersion`** (major.minor) with
  a hard compatibility contract: a new minor version may only *add* fields, and every added field
  must have a sensible default, so that metadata can always be round-tripped between any two
  minor versions of the same major version (see `doc/source/file_formats/eggs.rst.inc` and the
  `--metadata-version` flag on the CLI, which re-renders spec/depend at an arbitrary version).
  When modifying `EggMetadata` fields, preserve that forward/backward-compatibility guarantee.
  `_package_info.py` handles the PKG-INFO metadata; `egg.py` provides `EggBuilder`/`EggRewriter`
  for producing/rewriting egg archives; `legacy.py` guesses tags (abi/platform/python) for older
  eggs that predate explicit tagging; `_blacklist/` holds hardcoded exceptions for known-bad or
  ambiguous historical package metadata; `setuptools_egg.py` and `_wheel_info.py`/
  `_wheel_common.py` bridge to non-Enthought package formats.

- **`okonomiyaki/runtimes/`** — metadata for Enthought Python runtime archives (as opposed to
  package eggs): `runtime_metadata.py` defines the `IRuntimeMetadata` interface and path
  validation, `runtime.py`/`runtime_info.py` model runtime instances, `runtime_schemas.py` holds
  the JSON schema(s) used for validation.

- **`okonomiyaki/utils/`** — shared helpers (`compute_sha256`, `parse_assignments`, etc.) and
  `test_data/`, which bundles real sample eggs/wheels/runtimes (organized by platform/cpython
  version under `eggs/<platform>/<cpython>/*.egg`) used as fixtures across the test suite.

- **`okonomiyaki/errors.py`** — all exceptions inherit from `OkonomiyakiError`; format-specific
  errors generally carry the offending value as an attribute (e.g. `InvalidEggName.egg_name`,
  `InvalidMetadataField.name`/`.value`) rather than only a message string.

Cross-cutting convention: most public value types (versions, platform/arch objects, some egg
metadata pieces) are immutable and implement equality/ordering/hashing explicitly rather than via
`@dataclass` — match this pattern for new value types instead of introducing a different one.
