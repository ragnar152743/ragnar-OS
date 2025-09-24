"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "356034bb28c51b7b181f6d65771da4795d966e8d9774a0ba59520474fe8b674f",
    "mini_os/__init__.py": "c9701621c2af445dd347c7c6f2fbe64a9a65eab0925441c97b383af9561c49f2",
    "mini_os/all_in_one.py": "7b4f9722debf7ae34f6df2d5a5c3872d1111305a97faf04e8ef1760abe2b96cb",
    "mini_os/applications.py": "22919c6e709261510e0566024544d3e59c03f60d0338223ae3d9af84b389193d",
    "mini_os/boot.py": "165da8c63584b6809d65ef208a5b879bf293837ec8250ca294963713360c3200",
    "mini_os/interfaces.py": "e06511d2feb2f2c3f0f1eb413341fcf29ea7864a9b51ff4c48a72c487f32ebb5",
    "mini_os/maintenance.py": "2ff46bf888bf66653898cf738055120c8c907aefb3b2c226a748bc48fba7327a",
    "mini_os/loading.py": "1e8cb1ff56541c481b63b3c852890d60b0f7f77eb678ae5947b9f4f8f09e47b5",
    "mini_os/gui.py": "8ceb847be0c26e758fe0cba510dbf4c9dd4771e293373b4a4dd0c9d97c9d176e",
    "mini_os/localization.py": "29e5a4fbd8b99d8728cf50b6241af3ba8755be1c8af15494d683217af2644f25",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
