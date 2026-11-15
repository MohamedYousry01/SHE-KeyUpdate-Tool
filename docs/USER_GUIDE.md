# SHE Key Studio user guide

SHE Key Studio prepares encrypted, authenticated updates for SHE-compatible
hardware. You provide the current authorization secret and the replacement
key; the application produces the protocol messages your firmware will send.
It does not retrieve secrets from hardware, install drivers, or send diagnostic commands.

## Start in two minutes

1. Run `SHE-Key-Studio.exe` on 64-bit Windows.
2. Click **Load public demo**. All five messages appear. Keys stay masked.
3. Compare the bytes with the README example. Export JSON or a C header.
4. For your own device, replace both keys and the UID, choose the correct
   target, authorization slot, counter, flag profile, and bank, then Generate.

The public demo uses intentionally public, fixed keys. Never provision these
keys into a device whose security matters. **Random** generates a new key;
it does not generate or replace the device's existing authorization secret.
Before provisioning, retain a required new secret in your approved secure key
store. The application does not save it for you, and future self-authorized
updates may require that key.

## Input fields

| Field | Meaning | Format |
|---|---|---|
| Device UID | Device identifier read using your platform tooling | 15 bytes / 30 hex characters |
| Authentication key | Current secret in the selected authorization slot | 16 bytes / 32 hex characters |
| New key | Replacement AES-128 key or BOOT_MAC value | 16 bytes / 32 hex characters |
| Target wire slot | Slot to update | Named slot with hexadecimal wire ID |
| Authorization slot | Slot holding the supplied current secret | Filtered by target |
| Counter | Proposed new per-slot counter | Decimal or `0x` hex, 1–268435455 for nonvolatile slots |
| Profile | Transmitted flag layout | `she5` or `extended6` |
| Bank | KDF constant selection | 1 standard, 2 device extension |

Hex fields accept spaces, underscores, uppercase/lowercase, and one leading
`0x`. They do not accept C array syntax or comma-separated bytes.
Use the UID's documented byte order; values are serialized most significant byte first.

The new counter must be strictly greater than the value stored in the target
slot. The application cannot read that value. Do not automatically increment
your provisioning database until hardware success is confirmed. RAM_KEY
requires **counter 0 and flags 0**; choosing it sets these values for you.

For self-authorized initial provisioning, the empty-slot value depends on your
device. Do not assume an erased key is zero; consult its reference manual.

## Select a profile and bank

- **SHE, 5 flags:** WRITE_PROTECTION, BOOT_PROTECTION, DEBUGGER_PROTECTION,
  KEY_USAGE, WILDCARD; five bits followed by 95 zero bits in M2 metadata.
- **Extended, 6 flags:** same order plus VERIFY_ONLY; six bits followed by
  94 zero bits. This is an explicitly selected extension, not auto-detected.
- **Bank 1:** standard SHE constants and KEY_1–KEY_10 at wire IDs 4–13.
- **Bank 2:** extension constants and KEY_11–KEY_20 at the same wire IDs.
  For example, bank 2 plus wire ID 4 selects logical KEY_11. Authorization
  selection for self-update refers to that bank's current slot.

Check your hardware/firmware manual before selecting an extension. The profile
and bank are carried as JSON metadata; neither is encoded as a separate M1 field.
Some flag patterns are indistinguishable between layouts, so successful parsing
cannot establish which layout the sender intended.

## Protection flags

| Flag set to 1 | Effect on a supporting target |
|---|---|
| WRITE_PROTECTION | Permanently prevent further updates of the physical slot |
| BOOT_PROTECTION | Disable key use if secure boot conditions are not satisfied |
| DEBUGGER_PROTECTION | Disable key use when the external debugger is active |
| KEY_USAGE | Select CMAC use rather than encryption/decryption |
| WILDCARD | Disable future wildcard UID updates of the slot |
| VERIFY_ONLY | Extension restricting CMAC to verification; meaningful with KEY_USAGE |

Flags only take effect when hardware accepts the request. Hardware can ignore
flags that are inapplicable to a particular slot; consult the slot's policy.
WILDCARD=1 **disables** wildcard usage. An all-zero UID in the current request
is accepted only if the device's already-stored policy allows it.

## Generate, export, and apply

1. Click **Generate M1–M5**. If validation fails, the status bar identifies the field.
2. Copy an individual message or export a bundle:
   - **JSON:** versioned metadata and uppercase M1–M5 strings.
   - **C header:** standard `uint8_t`, `static const` arrays and `<stdint.h>`;
     include it directly from your embedded application.
   - **Text:** message names, lengths, and hex strings.
3. Through your own firmware/API, supply M1 (16 bytes), M2 (32), M3 (16)
   to the target's key-load command. A transport may concatenate them into
   a 64-byte payload; framing and diagnostics remain target-specific.
4. Read the ECU response and verify it as described below.

Editing any generator field invalidates displayed results and disables exports.
This prevents accidentally exporting messages for an earlier key or counter.
Exports omit the plaintext authentication key, new key, and derived keys.
Provisioning bundles are still sensitive and should be access-controlled.

## Inspect an existing update

1. Open **Inspect messages** and import/paste an exported JSON bundle.
2. Enter the corresponding authentication key. **Use generated bundle** copies
   only the message bundle; enter the secret separately.
3. Click **Authenticate & inspect**. M3 must verify before M2 is decrypted.
4. Review recovered UID, IDs, counter, flags, profile, and bank. If needed,
   explicitly reveal the recovered new key in this session.

The inspector requires M3. Unauthenticated M1/M2 decryption is deliberately
not offered. Changing inspection inputs removes the previous recovered result.

## Verify an actual response

1. Generate the exact request corresponding to the hardware operation.
2. Open **Verify ECU proof**.
3. Paste **received** M4 (32 bytes) and M5 (16 bytes), then Verify.
4. Both must match the request. Record success in your provisioning records
   only when you trust the transport and the hardware operation.

Copying generated M4/M5 back into this screen merely tests the application
against itself. It does not prove a device changed its memory.

## Session privacy

Keys are masked by default. No network communication, autosave, analytics,
key history, or automatic disk logs are implemented. Copy buttons write
messages to the Windows clipboard and clear them after 30 seconds if unchanged.
An existing clipboard manager may retain copies. **Clear session** clears key,
inspection, and proof fields and the application's current clipboard value.
Python and Qt do not guarantee memory zeroization; this is a developer utility,
not a certified provisioning appliance or hardware-backed keystore.

## Troubleshooting

| Symptom | Check |
|---|---|
| Hex length error | UID is 30 hex characters; keys are 32; do not add C array punctuation |
| M3 authentication failure | Exact auth key, complete M1–M3, bank, and byte order |
| Reserved bits nonzero | Flag layout selection and message authenticity |
| Valid messages rejected by ECU | Stored counter, correct UID, auth slot populated, slot protection, platform-specific policies |
| Proof mismatch | Actual returned bytes, request counter/key/UID/IDs, bank selection, transport byte order |
| RAM_KEY rejected locally | Counter and every flag must be zero |
| Startup takes a few seconds | One-file runtime extraction on first launch |

Author: [Mohamed Yousry — portfolio](https://mohamedyousry01.github.io/Mohamed-Yousry-Portfolio/).
