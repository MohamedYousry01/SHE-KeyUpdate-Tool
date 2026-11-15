# Validation scope

Local validation uses Windows x64 and Python 3.14 with the pinned dependencies.
The automated suite contains **54 passing tests**. Parameterized loops additionally
exercise **1,344 protocol combinations** across all flag masks, both profiles,
two banks, and seven counters, checking generation, wire-bit layout, authenticated
inspection, and proof verification for each combination.

Coverage includes:

- Fixed public M1–M5 example and known encryption/MAC derivation outputs.
- Every five-flag and six-flag mask.
- Counters 1, 15, 16, 255, 256, 65537, and 268435455.
- Bank 1 and the optional bank 2 derivation constants.
- Altered M1/M2/M3 rejection; wrong authentication key and wrong bank rejection.
- Altered proof rejection and strict field/length/slot validation.
- RAM_KEY zero counter/flags and SECRET_KEY authorization.
- C/JSON/text exports excluding plaintext keys.
- CLI generation, authenticated inspection, successful proof and failed proof.
- Desktop demo loading, inspection, explicit key reveal, proof checking,
  invalidation after edits, and session clearing.

Executable checks run separately from source tests. The frozen GUI's offscreen
self-check loads Qt, generates a known vector, inspects it, verifies its proof,
and clears its session. The native Windows desktop startup is checked locally.
The frozen CLI is checked against the known vector. The Windows workflow
repeats the tests and frozen executable checks.
SHA-256 checksums identify the binaries in each build; they are integrity
checks, not a digital publisher signature.

This is software-level validation. No physical ECU acceptance, vendor
certification, secure manufacturing integration, or independent cryptographic
audit is claimed. Hardware policy, persistent counter state, and transport
integration must be validated on the intended target.
