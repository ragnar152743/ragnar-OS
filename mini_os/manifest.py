"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "e4625b785031bdeaa28de30a7ab348319a52aadde4527829cc1d41430f3a38fb",
    "mini_os/__init__.py": "02f8a62bf0de6ec8ddcfa60468ec6902119eaf42d3887189e2bb7e6cccdd2789",
    "mini_os/all_in_one.py": "d78e3b577b82486457c44e12ee41bcc0ccafd6927d58e62d8f7788f7d4f2fd7e",
    "mini_os/applications.py": "22919c6e709261510e0566024544d3e59c03f60d0338223ae3d9af84b389193d",
    "mini_os/boot.py": "f5a88dcc95fbba627f37162aef356f0b39912593492ec40d46c804c7b3d70564",
    "mini_os/interfaces.py": "65693d11471001ab6f995df543ed6dcad73f1a0d63515ad7a5180a7b0bff1357",
    "mini_os/maintenance.py": "35f98c9b51d8ca316651ed7d03d9428d66859e0738c5aae11bec67d660a37ff8",
    "mini_os/loading.py": "226142143547b861f32b944f1adb665ff6ac9d2c93eb2a311e3831966c1b339f",
    "mini_os/gui.py": "ca911a8834ba3b2957ae9161c43e21d77597c73fdd44fe1eb30a755d4249b440",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
