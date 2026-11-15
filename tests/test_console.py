import json
from she_studio.console import main


def test_cli_generate_inspect_verify(tmp_path):
    data = {"uid":"00"*14+"01","auth_key":bytes(range(16)).hex(),"new_key":bytes(reversed(range(16))).hex()}
    source = tmp_path/"input.json"; source.write_text(json.dumps(data))
    output = tmp_path/"output.json"
    assert main(["generate",str(source),"--output",str(output)]) == 0
    bundle = json.loads(output.read_text())
    source.write_text(json.dumps({"auth_key":data["auth_key"],**bundle["messages"]}))
    inspected = tmp_path/"inspected.json"
    assert main(["inspect",str(source),"--output",str(inspected)]) == 0
    assert json.loads(inspected.read_text())["counter"] == 1
    source.write_text(json.dumps({"request":data,"M4":bundle["messages"]["M4"],"M5":bundle["messages"]["M5"]}))
    assert main(["verify",str(source),"--output",str(tmp_path/"proof.json")]) == 0
    source.write_text(json.dumps({"request":data,"M4":bundle["messages"]["M4"],"M5":"00"*16}))
    assert main(["verify",str(source),"--output",str(tmp_path/"badproof.json")]) == 2
