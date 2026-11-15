"""Pure protocol operations. No UI, persistence, or hardware access."""
from dataclasses import dataclass, field
import hmac
import re
from Crypto.Cipher import AES
from Crypto.Hash import CMAC

PROFILES = {"she5": 5, "extended6": 6}
SLOTS = {1: "MASTER_ECU_KEY", 2: "BOOT_MAC_KEY", 3: "BOOT_MAC",
         **{n + 3: f"KEY_{n}" for n in range(1, 11)}, 14: "RAM_KEY"}
FLAG_NAMES = ("WRITE_PROTECTION", "BOOT_PROTECTION", "DEBUGGER_PROTECTION",
              "KEY_USAGE", "WILDCARD", "VERIFY_ONLY")


def hex_bytes(value: str, length: int, label: str = "Value") -> bytes:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a hex string.")
    value = re.sub(r"[\s_]", "", value.strip())
    if value.lower().startswith("0x"):
        value = value[2:]
    if len(value) != length * 2 or not re.fullmatch(r"[0-9a-fA-F]+", value):
        raise ValueError(f"{label} requires exactly {length * 2} hexadecimal characters ({length} bytes).")
    return bytes.fromhex(value)


def integer(value, label: str) -> int:
    try:
        if type(value) is int:
            return value
        if isinstance(value, str):
            return int(value, 16 if value.lower().startswith("0x") else 10)
    except ValueError:
        pass
    raise ValueError(f"{label} must be a decimal integer or a 0x-prefixed integer.")


def flag_width(profile: str) -> int:
    if profile not in PROFILES:
        raise ValueError("Profile must be she5 or extended6.")
    return PROFILES[profile]


def derive(key: bytes, purpose: int, bank: int = 1) -> bytes:
    """AES-MP over K || pre-padded C; do not pad C again."""
    if len(key) != 16 or purpose not in (1, 2) or bank not in (1, 2):
        raise ValueError("Invalid key derivation parameters.")
    constant = bytes([1, purpose | (0x80 if bank == 2 else 0)]) + b"SHE\x00\x80" + bytes(8) + b"\xb0"
    state = bytes(16)
    for block in (key, constant):
        encrypted = AES.new(state, AES.MODE_ECB).encrypt(block)
        state = bytes(a ^ b ^ c for a, b, c in zip(state, block, encrypted))
    return state


def mac(key: bytes, message: bytes) -> bytes:
    return CMAC.new(key, msg=message, ciphermod=AES).digest()


@dataclass(frozen=True)
class Provisioning:
    uid: bytes
    new_key: bytes = field(repr=False)
    auth_key: bytes = field(repr=False)
    slot: int = 4
    auth_slot: int = 1
    counter: int = 1
    flags: int = 0
    profile: str = "she5"
    bank: int = 1

    def __post_init__(self):
        for name, size in (("uid", 15), ("new_key", 16), ("auth_key", 16)):
            if not isinstance(getattr(self, name), bytes) or len(getattr(self, name)) != size:
                raise ValueError(f"{name} must be {size} bytes.")
        width = flag_width(self.profile)
        for name, lo, hi in (("slot", 1, 14), ("auth_slot", 0, 14), ("counter", 0, 0xfffffff),
                             ("flags", 0, (1 << width) - 1), ("bank", 1, 2)):
            val = getattr(self, name)
            if type(val) is not int or not lo <= val <= hi:
                raise ValueError(f"{name} must be in {lo}..{hi}.")
        allowed = {1, self.slot}
        if self.slot == 3:
            allowed = {1, 2}
        if self.slot == 14:
            allowed = set(range(15)) - {3}
        if self.auth_slot not in allowed:
            raise ValueError("Authentication slot cannot authorize this target slot.")
        if self.slot == 14 and (self.counter or self.flags):
            raise ValueError("RAM_KEY requires counter=0 and flags=0.")
        if self.slot != 14 and self.counter == 0:
            raise ValueError("A nonvolatile update needs a counter greater than zero.")
        if self.bank == 2 and not 4 <= self.slot <= 13:
            raise ValueError("Bank 2 is available only for KEY_11..KEY_20 (wire slots 4..13).")

    @classmethod
    def from_dict(cls, data):
        allowed = {"uid", "new_key", "auth_key", "slot", "auth_slot", "counter", "flags", "profile", "bank"}
        if not isinstance(data, dict) or set(data) - allowed:
            raise ValueError("Input must be an object with documented provisioning fields only.")
        values = dict(data)
        for name, size in (("uid", 15), ("new_key", 16), ("auth_key", 16)):
            values[name] = hex_bytes(values.get(name, ""), size, name)
        for name in ("slot", "auth_slot", "counter", "flags", "bank"):
            if name in values:
                values[name] = integer(values[name], name)
        return cls(**values)


def generate(request: Provisioning) -> dict[str, bytes]:
    width = flag_width(request.profile)
    m1 = request.uid + bytes([(request.slot << 4) | request.auth_slot])
    metadata = (request.counter << 100) | (request.flags << (100 - width))
    payload = metadata.to_bytes(16, "big") + request.new_key
    m2 = AES.new(derive(request.auth_key, 1, request.bank), AES.MODE_CBC, iv=bytes(16)).encrypt(payload)
    m3 = mac(derive(request.auth_key, 2, request.bank), m1 + m2)
    proof_block = ((request.counter << 100) | (1 << 99)).to_bytes(16, "big")
    m4 = m1 + AES.new(derive(request.new_key, 1, request.bank), AES.MODE_ECB).encrypt(proof_block)
    return {"M1": m1, "M2": m2, "M3": m3, "M4": m4,
            "M5": mac(derive(request.new_key, 2, request.bank), m4)}


def inspect_update(auth_key: bytes, m1: bytes, m2: bytes, m3: bytes,
                   profile: str = "she5", bank: int = 1) -> Provisioning:
    width = flag_width(profile)
    if (len(m1), len(m2), len(m3)) != (16, 32, 16):
        raise ValueError("M1 / M2 / M3 must be 16 / 32 / 16 bytes.")
    if not hmac.compare_digest(mac(derive(auth_key, 2, bank), m1 + m2), m3):
        raise ValueError("M3 authentication failed. Check the key, bank, and message bytes.")
    plain = AES.new(derive(auth_key, 1, bank), AES.MODE_CBC, iv=bytes(16)).decrypt(m2)
    header = int.from_bytes(plain[:16], "big")
    if header & ((1 << (100 - width)) - 1):
        raise ValueError("Reserved bits are nonzero. Check the selected flag profile.")
    return Provisioning(m1[:15], plain[16:], auth_key, m1[15] >> 4, m1[15] & 15,
                        header >> 100, (header >> (100 - width)) & ((1 << width) - 1), profile, bank)


def verify_proof(request: Provisioning, m4: bytes, m5: bytes) -> bool:
    if (len(m4), len(m5)) != (32, 16):
        raise ValueError("M4 / M5 must be 32 / 16 bytes.")
    expected = generate(request)
    match4 = hmac.compare_digest(expected["M4"], m4)
    match5 = hmac.compare_digest(expected["M5"], m5)
    return match4 & match5
