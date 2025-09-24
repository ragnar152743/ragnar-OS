"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "9400a9efbfd01300b74ebeb48e08415e3f7475026cb9e7374a111a632283e010",
    "mini_os/__init__.py": "51391dd3784f4ed019bf116d7eef1870d3d38713996de995989b419b14a6c9d4",
    "mini_os/all_in_one.py": "3e9199f52dcdc842d21136054ddeaebeeea009e2f0affe581a024e7417955394",
    "mini_os/applications.py": "22919c6e709261510e0566024544d3e59c03f60d0338223ae3d9af84b389193d",
    "mini_os/boot.py": "4061bdc1d4336d6098f983dae06a11f3b050a5f1e402b4ccf00f869830e2c20a",
    "mini_os/interfaces.py": "cd96b45cd5b922e580f45a5dfb0046da0e5887e3aec1e2c6796b86cf5b8eabd3",
    "mini_os/maintenance.py": "35f98c9b51d8ca316651ed7d03d9428d66859e0738c5aae11bec67d660a37ff8",
    "mini_os/loading.py": "226142143547b861f32b944f1adb665ff6ac9d2c93eb2a311e3831966c1b339f",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
