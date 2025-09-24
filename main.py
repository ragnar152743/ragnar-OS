"""Entry point for showcasing the Ragnar Mini OS."""

from __future__ import annotations

import argparse

from mini_os import BootReport, MiniOS, boot_sequence


def _run_text_demo(os_instance: MiniOS, report: BootReport) -> None:
    translator = os_instance.language_manager.translate
    print(report.splash)
    print()
    print(report.summary())
    print()
    if not report.ready:
        print(translator("boot_failure_abort"))
        return

    print(translator("demo_description"))
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
        print(translator("demo_launching", application=app_name))
        print(os_instance.open_application(app_name))
        print()


def run_demo(text_only: bool = False) -> None:
    os_instance, report = boot_sequence()
    if text_only:
        _run_text_demo(os_instance, report)
        return

    try:
        from mini_os.gui import MiniOSGui
    except Exception as exc:  # pragma: no cover - Tk may be missing
        print("Graphical UI unavailable (", exc, ") – falling back to text mode.")
        _run_text_demo(os_instance, report)
        return

    if not MiniOSGui.is_supported():
        print("Graphical UI not supported in this environment. Using text mode.")
        _run_text_demo(os_instance, report)
        return

    try:
        gui = MiniOSGui(os_instance, report)
    except RuntimeError as exc:  # pragma: no cover - environment guard
        print(exc)
        print("Falling back to text mode.")
        _run_text_demo(os_instance, report)
        return

    gui.run()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Ragnar Mini OS demo.")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Boot the Mini OS and show the interface/app demonstrations.",
    )
    parser.add_argument(
        "--text",
        action="store_true",
        help="Render the textual fallback UI instead of the graphical desktop.",
    )
    args = parser.parse_args()

    if args.demo:
        run_demo(text_only=args.text)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
