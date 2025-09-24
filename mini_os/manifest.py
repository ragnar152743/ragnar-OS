"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "637c8c27402e54d8e5b80306902f1d5c87c53a9947e7f618ce80bb2c3266fd69",
    "mini_os/__init__.py": "51391dd3784f4ed019bf116d7eef1870d3d38713996de995989b419b14a6c9d4",
    "mini_os/all_in_one.py": "d78e3b577b82486457c44e12ee41bcc0ccafd6927d58e62d8f7788f7d4f2fd7e",
    "mini_os/applications.py": "22919c6e709261510e0566024544d3e59c03f60d0338223ae3d9af84b389193d",
    "mini_os/boot.py": "f5a88dcc95fbba627f37162aef356f0b39912593492ec40d46c804c7b3d70564",
    "mini_os/interfaces.py": "ceac1fa80870d6b797df74efc4dbab92b0ac7d2eda1e8298b7f1e27a50b68d4a",
    "mini_os/maintenance.py": "35f98c9b51d8ca316651ed7d03d9428d66859e0738c5aae11bec67d660a37ff8",
    "mini_os/loading.py": "226142143547b861f32b944f1adb665ff6ac9d2c93eb2a311e3831966c1b339f",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
