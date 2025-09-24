"""Entry point for showcasing the Ragnar Mini OS."""

from __future__ import annotations

import argparse

from mini_os import MiniOS, boot_sequence


def run_demo() -> None:
    os_instance, report = boot_sequence()
    print(report.splash)
    print()
    print(report.summary())
    print()
    if not report.ready:
        print("Boot failed integrity verification. Aborting demo launch.")
        return

    print(os_instance.describe())
    print()
    print(os_instance.render_desktop())
    print()
    print(os_instance.render_start_menu())
    print()
    print(os_instance.render_home())
    print(os_instance.render_app_menu())
    print()
    for app_name in os_instance.list_app_names():
        print(f"Launching {app_name}...")
        print(os_instance.open_application(app_name))
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Ragnar Mini OS demo.")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Boot the Mini OS and show the interface/app demonstrations.",
    )
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
