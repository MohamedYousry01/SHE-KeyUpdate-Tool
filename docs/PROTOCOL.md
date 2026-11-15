# Protocol and interoperability reference

This document describes the implemented wire format. All integers and bytes
are in network/MSB-first order. It is an implementation guide, not a copy of
a standards document or a claim of platform certification.

## Sources

- [AUTOSAR SHE R22-11](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_TR_SecureHardwareExtensions.pdf): algorithm, memory-slot, key-load, memory-update, constant, and overview sections.
- [SHE known issues R22-11](https://www.autosar.org/fileadmin/standards/R22-11/FO/AUTOSAR_TR_ListOfKnownIssuesSecureHardwareExtensions.pdf): published amendments and errata.
- [NXP AN4234](https://www.nxp.com/docs/en/application-note/AN4234.pdf): CSE integration background.
- [Vector key-update reference](https://support.vector.com/sys_attachment.do?sys_id=534d25eb87548590b9f233770cbb3550): developer integration context.
- [NIST SP 800-38B](https://csrc.nist.gov/pubs/sp/800/38/b/upd1/final): AES-CMAC.

The default five-flag format is the baseline. Six flags and a second bank are
explicit extension profiles, requiring confirmation against the target's manual.

## Key derivation

Let `E(k, x)` be AES-128 ECB encryption of a 16-byte block. Initialize `h=0^128`.
For each block `x` of `key || constant`, compute `h = E(h,x) XOR h XOR x`.
The resulting `h` is the derived key. The constants below are already padded;
there is no additional block or PKCS#7 padding.

| Bank | Encryption constant | MAC constant |
|---|---|---|
| 1 | `010153484500800000000000000000B0` | `010253484500800000000000000000B0` |
| 2, extension | `018153484500800000000000000000B0` | `018253484500800000000000000000B0` |

`K1 = KDF(auth_key, ENC_C)`, `K2 = KDF(auth_key, MAC_C)`.
`K3 = KDF(new_key, ENC_C)`, `K4 = KDF(new_key, MAC_C)`.
K1–K4 are transient implementation values and never exported.

## Messages

| Message | Bytes | Construction |
|---|---:|---|
| M1 | 16 | 15-byte UID followed by `(target_id << 4) OR auth_id` |
| M2 | 32 | AES-CBC(K1, zero IV) over metadata block followed by new key |
| M3 | 16 | AES-CMAC(K2, M1 concatenated with M2) |
| M4 | 32 | M1 concatenated with AES-ECB(K3, padded counter) |
| M5 | 16 | AES-CMAC(K4, M4) |

M2 metadata is a 28-bit counter, then the selected flag bits, then zeroes to
fill the first 128-bit block. In numeric terms:

```text
she5:      metadata = (counter << 100) OR (flags << 95)
extended6: metadata = (counter << 100) OR (flags << 94)
```

In both profiles the M4 counter block is `(counter << 100) OR (1 << 99)`.
The single one bit pads the counter for the proof operation. M2 uses exactly
two blocks; no third block is appended.

Flag order from most to least significant transmitted bit:

```text
she5:      WRITE | BOOT | DEBUG | KEY_USAGE | WILDCARD
extended6: WRITE | BOOT | DEBUG | KEY_USAGE | WILDCARD | VERIFY_ONLY
```

The five baseline protection bits have identical wire positions between the
two profiles. VERIFY_ONLY occupies the next formerly reserved bit. Numeric
flag masks differ: WRITE is 16 in `she5`, 32 in `extended6`.
If VERIFY_ONLY is zero, the same five semantic flag settings produce the
same bytes in both profiles. The inspector cannot infer a profile from this.

## Slot model

| Wire ID | Bank 1 meaning | Update authorizers accepted locally |
|---|---|---|
| 0 | SECRET_KEY | Not an update target |
| 1 | MASTER_ECU_KEY | 1 |
| 2 | BOOT_MAC_KEY | 1 or 2 |
| 3 | BOOT_MAC | 1 or 2 |
| 4–13 | KEY_1–KEY_10 | 1 or same wire ID |
| 14 | RAM_KEY | Any 0–14 except BOOT_MAC (3) |
| 15 | Reserved | Rejected |

Bank 2 is accepted only for target wire IDs 4–13, mapping to logical keys
11–20. The selected bank affects all four derivations. IDs in the API/CLI
are always **wire IDs**, never logical key numbers. The GUI displays them.

RAM_KEY requires counter=0 and flags=0. Nonvolatile updates require a positive
28-bit counter. A local generator cannot evaluate empty-slot state, stored
protections, current counter, debug/boot status, memory faults, or device-specific
additional authorization restrictions.

## Inspection and proof verification

Inspection enforces M1/M2/M3 lengths and authenticates M3 in constant time
before decrypting. It rejects nonzero reserved bits and invalid decoded fields.
It reconstructs the full 28-bit counter, including across byte boundaries.

Proof verification recomputes expected M4 and M5 for the supplied request,
compares both using constant-time comparison, and requires both to match.
No input normalization changes byte order or silently truncates values.

Use an actual device response for verification. The application offers no
freshness database and cannot establish that a supplied proof came from hardware.
