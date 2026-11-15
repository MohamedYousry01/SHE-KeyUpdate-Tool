# Development and builds

## Requirements

Use 64-bit Windows 10/11, Python 3.14 x64, and Git. The source package supports
Python 3.10+, but the documented binary build uses 3.14. Qt and PyCryptodome
are installed from their published wheels. No Visual Studio compiler is needed
for this build path.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe launch.py
```

## Source boundaries

```text
she_studio/
  engine.py       Immutable provisioning inputs, KDF, generation, inspection, proof
  exchange.py     Versioned JSON, text, standard C exports
  console.py      File-based command interface
  desktop.py      Qt screens, field state, session and clipboard handling
tests/
  test_protocol.py
  test_console.py
  test_desktop.py
scripts/
  build.py        Windows executable and portable ZIP build
  preview.py      Public-demo screenshot generation
```

The engine has no UI, network, filesystem, or hardware dependencies. The desktop
and CLI call the same engine. Desktop edits invalidate generated output; inspection
edits invalidate recovered secrets. Exporters receive a validated request and its
messages and never serialize raw key attributes.

AES/CMAC primitives use PyCryptodome. Protocol packing, derivation composition,
validation, and application behavior live in this repository. Qt handles native
window rendering, accessibility, focus, and DPI scaling.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Desktop tests run Qt offscreen. Protocol tests exercise all 32/64 flag masks,
seven counter boundaries, and both banks, with authenticated decode round trips
and an independent bit-string assertion for the decrypted wire header. They also
cover the known public M1–M5 vector, key derivations, tampering, wrong key/bank,
proof mismatches, validation, RAM_KEY, and plaintext omission from exports.
The CLI test performs generate → inspect → verify and verifies failure behavior.

To refresh the README screenshot from the application's own widgets:

```powershell
.\.venv\Scripts\python.exe scripts\preview.py
```

The screenshot contains only public example data. It loads installed Windows
fonts explicitly because the offscreen Qt platform may not enumerate them.

## Standalone build

```powershell
.\.venv\Scripts\python.exe scripts\build.py
```

The script tests first, creates the icon, builds separate one-file GUI and CLI
executables, copies dependency notices, writes executable SHA-256 checksums,
and assembles a portable archive. Qt binaries are dynamically loaded when the
GUI executable extracts to a temporary folder. The CLI does not import Qt.
The packaging subprocess uses a restricted PATH containing Python and Windows
system directories to avoid bundling unrelated native DLLs from developer tools.
It also runs the frozen GUI with `--self-check`: Qt must load successfully,
generate the known vector, authenticate its update, verify its proof, and clear
its session. The check runs offscreen and returns exit code zero on success.

| Output | Purpose |
|---|---|
| `downloads/SHE-Key-Studio.exe` | Standalone windowed application |
| `downloads/she-key.exe` | Standalone console application |
| `downloads/SHA256SUMS.txt` | Executable integrity hashes |
| `release/SHE-Key-Studio-1.0.0-Windows-x64.zip` | Portable package with documentation, samples, licenses |

For a version change, update `pyproject.toml`, `she_studio/__init__.py`, the
desktop version labels, the build archive name, and release notes together.
The build uses pinned top-level requirements. It is repeatable, but not claimed
to produce byte-identical binaries across environments. Inspect dependency
updates and run the complete suite before rebuilding. Executables are unsigned;
code signing requires a publisher certificate supplied by the maintainer.

## Automated checks

The Windows GitHub Actions job installs dependencies, runs the same build and
tests, smoke-tests the frozen CLI, and uploads artifacts. Version tags also
publish a release with both executables, checksums, and the portable ZIP.
The Ubuntu job only publishes Windows assets; no Linux application is built.

## Contribution guidelines

Keep protocol changes separate from UI changes. Include a failing test for a
reproducible protocol bug. Use only public synthetic keys in issues and tests.
Document vendor extensions explicitly; do not silently change default wire
packing. Preserve source and license notices for redistributed dependencies.
