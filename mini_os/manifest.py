"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "30f19c763a416ac57bad6577c31fb9bf674c2dfa44f656256bc280b2949d0c33",
    "mini_os/__init__.py": "f8fdbde66a1cf84f97e6684f1c0ac747b8eb4bfe450a8002519d212a0892c2c9",
    "mini_os/all_in_one.py": "583431ff507925543440e8ba48ad7ff46719b4ebba1192ddacc8f6209e20b3fb",
    "mini_os/applications.py": "22919c6e709261510e0566024544d3e59c03f60d0338223ae3d9af84b389193d",
    "mini_os/boot.py": "6a076db40dbb62face2b8bdfa7bd47d352ddc18d15b8a5cf99172da5862d2af0",
    "mini_os/interfaces.py": "1db24bddb43debf43aa75f31585d4a7b3a139cb49e361b021bbc2c9a83d1ca46",
    "mini_os/maintenance.py": "35f98c9b51d8ca316651ed7d03d9428d66859e0738c5aae11bec67d660a37ff8",
    "mini_os/loading.py": "226142143547b861f32b944f1adb665ff6ac9d2c93eb2a311e3831966c1b339f",
    "mini_os/security.py": "06ab37f436d9c6c50c10a851686c143cdfcbd6454c153604d38f8206be5cb16f",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
