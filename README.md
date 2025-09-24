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
- **Neon user interface** – the home desktop now renders a vibrant, neon-inspired console UI with
  animated-style headers, iconography, and stylised panels for each widget.
- **Immersive desktop shell** – experience a faux Windows-like boot splash, a neon desktop covered in
  application icons, and a Start menu panel that highlights pinned and full application listings.

## Running the demo

### Python entry point

Run the demo with:

```bash
python main.py --demo
```

The command prints the boot splash and diagnostic report, describes the OS, renders the neon desktop,
shows the Start menu, displays the home widgets, lists the available applications, and sequentially
launches each app so you can inspect the generated output.

### Windows launcher

A `launcher.bat` script is provided for convenience. Double-clicking it (or running it from `cmd`)
will execute the same demo sequence on Windows and leave the console window open so you can review the
boot log and app output.
