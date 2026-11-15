# Security and key handling

SHE Key Studio is a local developer workbench. It does not access hardware,
retrieve ECU secrets, manage persistent key counters, or act as a key vault.

- All key calculations happen locally using PyCryptodome AES/CMAC.
- The desktop masks secret fields by default and does not automatically save them.
- No network, telemetry, automatic logs, or key history are implemented.
- M3 authentication is required before inspection decrypts M2.
- Exported bundles exclude plaintext and derived keys but remain sensitive.
- The CLI reads secrets from files; keep private files outside version control.
- Python/Qt memory copies are not guaranteed to be zeroized. An administrator,
  debugger, compromised OS, crash dump, or clipboard manager can expose data.
- Demo keys are public. Use fresh secrets and your organization's approved
  provisioning processes for real devices.
- Applying WRITE_PROTECTION on hardware can be irreversible.

Report a security issue privately through the repository's GitHub security
advisory feature if enabled. Otherwise use the contact route on the author's
[portfolio](https://mohamedyousry01.github.io/Mohamed-Yousry-Portfolio/).
Include a minimal reproduction with synthetic keys; never send production secrets.
