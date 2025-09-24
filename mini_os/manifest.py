"""Static manifest describing expected file hashes for integrity checks."""

from __future__ import annotations

EXPECTED_HASHES = {
    "main.py": "9400a9efbfd01300b74ebeb48e08415e3f7475026cb9e7374a111a632283e010",
    "mini_os/__init__.py": "12cd73833e6aee28dbfafa5605453878cd4f93c0a7eaeaadac7409dd406b8fa1",
    "mini_os/all_in_one.py": "678f88273c3247c9de0d93119d830da212f3daf06b7d468511ca3466450c9dd4",
    "mini_os/applications.py": "64f789c163a05532b6d9e7303101a2221235a77483748e885eac31e8d86992a7",
    "mini_os/boot.py": "cb6e55a3efd8900bc97ded9087cefd7422f75a5a48e5e3f75cbb71fba665ced6",
    "mini_os/interfaces.py": "1db24bddb43debf43aa75f31585d4a7b3a139cb49e361b021bbc2c9a83d1ca46",
    "mini_os/maintenance.py": "35f98c9b51d8ca316651ed7d03d9428d66859e0738c5aae11bec67d660a37ff8",
    "mini_os/loading.py": "226142143547b861f32b944f1adb665ff6ac9d2c93eb2a311e3831966c1b339f",
    "launcher.bat": "7994771fb92acbea33664b1d4329937674cfff618035ee0603b20edf2a94066f",
}


__all__ = ["EXPECTED_HASHES"]
