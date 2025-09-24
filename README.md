# Ragnar Mini OS

This repository contains a small Python-based "mini operating system" simulation. It demonstrates how
separate components can be organised to represent different responsibilities, such as managing the user
interfaces, applications, boot sequence, automated maintenance, and an all-in-one controller tying the
pieces together.

## Features

- **Boot diagnostics** – the system performs a SHA-256 integrity scan of key files before the OS is
  considered ready.
- **Startup file loading** – the boot sequence now streams through each critical MiniOS file, reporting
  simulated caching progress so you can observe the load order during startup.
- **Automatic maintenance guardian** – proactively checks that all applications respond, verifies
  widgets registered in the interface layer, and schedules simulated background tasks.
- **Rich application catalogue** – beyond the classic Notes, Terminal, and Settings apps, MiniOS ships
  calculator, weather, calendar, music, news, and system monitor experiences that generate contextual
  information at runtime.
- **Graphical desktop shell** – a full Tkinter desktop experience with animated splash screen, stylised
  launcher icons, widgets, and a Start menu featuring pinned and searchable app listings.
- **Neon user interface** – the text renderer remains available as a fallback, retaining the vibrant,
  neon-inspired styling for environments where a GUI cannot be launched.
- **Internationalised onboarding** – the first boot greets you with a multilingual language selector
  (English, Français, Español, Deutsch) and stores the preference for all subsequent sessions.

## Running the demo

### Python entry point

Run the demo with:

```bash
python main.py --demo
```

If Tkinter and a display server are available, this opens the graphical Ragnar MiniOS desktop – complete
with splash screen, neon taskbar, desktop icons, Start menu, widgets, and an application console that
shows live output as you launch apps.

If you are working inside a headless environment, add `--text` to force the colourful console fallback:

```bash
python main.py --demo --text
```

The text mode prints the boot report, describes the OS, renders the neon-styled console screens, and
launches each built-in application sequentially so you can inspect their output in the terminal. On the
very first run you will be asked to choose a language (or default to English when running non-
interactively); the selection is stored in `mini_os_state.json`.

### Windows launcher

A `launcher.bat` script is provided for convenience. Double-clicking it (or running it from `cmd`)
will execute the same demo sequence on Windows and leave the console window open so you can review the
boot log and app output.
