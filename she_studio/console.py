"""File-based CLI keeps keys out of process arguments and shell history."""
import argparse
import json
from pathlib import Path
from .engine import Provisioning, generate, inspect_update, hex_bytes, verify_proof
from .exchange import render


def main(argv=None):
    parser = argparse.ArgumentParser(description="SHE Key Studio offline CLI")
    parser.add_argument("command", choices=["generate", "inspect", "verify"])
    parser.add_argument("input", type=Path, help="Private input JSON; see docs/CLI.md")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--format", choices=["json", "text", "c"], default="json")
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        if args.command == "generate":
            request = Provisioning.from_dict(data)
            output = render(request, generate(request), args.format)
        elif args.command == "inspect":
            request = inspect_update(hex_bytes(data["auth_key"], 16, "auth_key"),
                *(hex_bytes(data[name], size, name) for name, size in (("M1",16),("M2",32),("M3",16))),
                data.get("profile", "she5"), data.get("bank", 1))
            output = json.dumps({"authenticated": True, "uid": request.uid.hex(), "slot": request.slot,
                "auth_slot": request.auth_slot, "counter": request.counter, "flags": request.flags,
                "profile": request.profile, "bank": request.bank}, indent=2) + "\n"
        else:
            request = Provisioning.from_dict(data["request"])
            valid = verify_proof(request, hex_bytes(data["M4"], 32, "M4"), hex_bytes(data["M5"],16,"M5"))
            output = json.dumps({"proof_valid": valid}) + "\n"
            if not valid:
                with args.output.open("x", encoding="utf-8") as stream:
                    stream.write(output)
                return 2
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(output)
        return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
