# Command-line interface

Use the standalone `downloads/she-key.exe`, or invoke
`python -m she_studio.console` from an installed source environment.
The GUI is `SHE-Key-Studio.exe`. Both use the same protocol engine.

Inputs are JSON files, keeping raw keys out of command arguments and shell
history. Store private inputs in the git-ignored `private/` folder and protect
them with appropriate Windows file permissions. Output files must not already
exist; the CLI refuses to overwrite them. GUI exports use a save dialog.

## Generate

```powershell
.\downloads\she-key.exe generate examples\demo-input.json --output update.json
.\downloads\she-key.exe generate examples\demo-input.json --format c --output update.h
.\downloads\she-key.exe generate examples\demo-input.json --format text --output update.txt
```

Input:

```json
{
  "uid": "000000000000000000000000000001",
  "auth_key": "000102030405060708090A0B0C0D0E0F",
  "new_key": "0F0E0D0C0B0A09080706050403020100",
  "slot": 4,
  "auth_slot": 1,
  "counter": 1,
  "flags": 0,
  "profile": "she5",
  "bank": 1
}
```

UID and both keys are required. Other fields default to the values shown.
Integers may be JSON numbers or decimal/`0x` strings. Unknown provisioning
fields are rejected to catch misspelled parameters. Slots are wire IDs.
For bank 2 KEY_11 use `slot:4, bank:2`. For RAM_KEY use `slot:14,
counter:0, flags:0` and an authorizer allowed by your target.

JSON output has schema `she-key-studio/v1`, public metadata, and a `messages`
object with M1–M5 hex strings. It never includes plaintext or derived keys.

## Inspect

Create a private input with `auth_key`, `M1`, `M2`, `M3`, `profile`, and `bank`
at the top level. Example below uses public demo data:

```json
{
  "auth_key": "000102030405060708090A0B0C0D0E0F",
  "M1": "00000000000000000000000000000141",
  "M2": "2B111E2D93F486566BCBBA1D7F7A9797C94643B050FC5D4D7DE14CFF682203C3",
  "M3": "B9D745E5ACE7D41860BC63C2B9F5BB46",
  "profile": "she5",
  "bank": 1
}
```

```powershell
.\downloads\she-key.exe inspect private\inspect.json --output inspected.json
```

The CLI inspection schema is flat; the GUI importer accepts the nested export
bundle. Inspection output contains authenticated UID, slot IDs, counter, flags,
profile, and bank. It does **not** write the decrypted new key. The GUI offers
an explicit in-session reveal for that purpose. `--format` applies only to Generate;
Inspect and Verify always emit JSON.

## Verify

Use a private input with `request` holding the complete generation input above,
and top-level `M4` and `M5` holding the actual device response as hex strings:

```text
{"request": { ... generation fields ... }, "M4": "64 hex characters", "M5": "32 hex characters"}
```

```powershell
.\downloads\she-key.exe verify private\proof.json --output proof-result.json
```

Output: `{"proof_valid": true}` or `{"proof_valid": false}`.

| Exit code | Meaning |
|---|---|
| 0 | Operation succeeded / proof matched |
| 1 | Validation, authentication, parsing, or file error |
| 2 | Proof mismatch; also argparse's code for invalid CLI syntax |

Do not use a generated expected proof as evidence of a hardware update.
