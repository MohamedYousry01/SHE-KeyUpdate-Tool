import json
from dataclasses import replace
import pytest
from Crypto.Cipher import AES
from she_studio.engine import Provisioning, generate, inspect_update, verify_proof, derive, mac, hex_bytes
from she_studio.exchange import render


@pytest.fixture
def request_vector():
    return Provisioning(bytes(14)+b"\x01",bytes(reversed(range(16))),bytes(range(16)))


def test_known_vector(request_vector):
    expected = ["00000000000000000000000000000141",
        "2b111e2d93f486566bcbba1d7f7a9797c94643b050fc5d4d7de14cff682203c3",
        "b9d745e5ace7d41860bc63c2b9f5bb46",
        "00000000000000000000000000000141b472e8d8727d70d57295e74849a27917",
        "820d8d95dc11b4668878160cb2a4e23e"]
    assert [x.hex() for x in generate(request_vector).values()] == expected
    assert derive(request_vector.auth_key,1).hex() == "118a46447a770d87828a69c222e2d17e"
    assert derive(request_vector.auth_key,2).hex() == "2ebb2a3da62dbd64b18ba6493e9fbe22"


@pytest.mark.parametrize("profile,width",[("she5",5),("extended6",6)])
@pytest.mark.parametrize("bank",[1,2])
@pytest.mark.parametrize("counter",[1,15,16,255,256,65537,0xfffffff])
def test_all_flag_values(request_vector,profile,width,bank,counter):
    for flags in range(1<<width):
        request = replace(request_vector,profile=profile,bank=bank,counter=counter,flags=flags)
        messages = generate(request)
        decoded = inspect_update(request.auth_key,*(messages[k] for k in ("M1","M2","M3")),profile,bank)
        assert decoded == request
        # Verify the exact wire bit allocation independently of the decoder.
        plaintext = AES.new(derive(request.auth_key,1,bank),AES.MODE_CBC,iv=bytes(16)).decrypt(messages["M2"])
        bits = f"{int.from_bytes(plaintext[:16],'big'):0128b}"
        assert bits == f"{counter:028b}{flags:0{width}b}" + "0"*(100-width)
        assert verify_proof(request,messages["M4"],messages["M5"])


@pytest.mark.parametrize("name",["M1","M2","M3"])
def test_tampering_rejected_before_decryption(request_vector,name):
    messages = generate(request_vector)
    changed = bytearray(messages[name]); changed[-1] ^= 1
    messages[name] = bytes(changed)
    with pytest.raises(ValueError,match="authentication failed"):
        inspect_update(request_vector.auth_key,*(messages[k] for k in ("M1","M2","M3")))


def test_wrong_key_and_bank(request_vector):
    messages = generate(request_vector)
    for key, bank in ((bytes(16),1),(request_vector.auth_key,2)):
        with pytest.raises(ValueError,match="authentication failed"):
            inspect_update(key,*(messages[k] for k in ("M1","M2","M3")),bank=bank)


@pytest.mark.parametrize("name",["M4","M5"])
def test_bad_proof(request_vector,name):
    messages = generate(request_vector)
    messages[name] = bytes(len(messages[name]))
    assert not verify_proof(request_vector,messages["M4"],messages["M5"])


@pytest.mark.parametrize("change",[{"counter":-1},{"counter":0},{"counter":0x10000000},
    {"slot":0},{"slot":15},{"flags":32},{"bank":3},{"auth_slot":2},{"uid":bytes(16)},
    {"new_key":bytes(15)},{"profile":"unknown"},{"counter":True},{"slot":14},{"slot":1,"bank":2}])
def test_invalid_requests(request_vector,change):
    with pytest.raises(ValueError):
        replace(request_vector,**change)


def test_ram(request_vector):
    request = replace(request_vector,slot=14,auth_slot=0,counter=0)
    messages = generate(request)
    assert inspect_update(request.auth_key,*(messages[k] for k in ("M1","M2","M3"))) == request


def test_exports_omit_plaintext_keys(request_vector):
    messages = generate(request_vector)
    for kind in ("json","text","c"):
        output = render(request_vector,messages,kind)
        assert request_vector.new_key.hex() not in output.lower()
        assert request_vector.auth_key.hex() not in output.lower()
    data = json.loads(render(request_vector,messages))
    assert len(bytes.fromhex(data["messages"]["M2"])) == 32
    with pytest.raises(ValueError):
        render(request_vector,messages,"c","bad-name")


def test_hex_parser():
    assert hex_bytes("0xAA_BB CC",3) == b"\xaa\xbb\xcc"
    for text in ("0x0","GG","", "0011"):
        with pytest.raises(ValueError):
            hex_bytes(text,1)
