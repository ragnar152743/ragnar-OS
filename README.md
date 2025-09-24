# Ragnar Mini OS

This repository contains a Python-based "mini operating system" simulation. The latest
iteration expands the toy environment into a feature-rich playground with kernel-like
services, declarative security, sandboxed applications, and a desktop shell facade.

## Features

- **Kernel-style coordination** – asynchronous process supervision, IPC messaging, a
  restart-aware service registry, per-application sandboxes, and a virtualization manager
  model the foundations of a modern userland.
- **Profiles and security** – PBKDF2-hashed logins, per-app API keys, declarative
  permission manifests, a vault for encrypted secrets, append-only audit logs, and a toy
  antivirus/threat monitor keep the environment controlled.
- **Applications & marketplace** – apps ship with manifests, lifecycle hooks, hot reload
  stubs, and install via a simulated marketplace plus RagnarPM package manager with
  lockfiles and offline mirrors.
- **UI surface** – a desktop shell facade powers widgets, notifications, launcher search,
  and control center toggles while maintaining compatibility with the textual interface
  used by the demo.
- **Storage & data tooling** – logical volumes, virtual storage snapshots, per-app SQLite
  stores, trash management, and no-code pipelines round out the developer toolkit.

## Running the demo

### Python entry point

Run the demo with:

```bash
python main.py --demo
```

The command prints the boot report, describes the OS, renders the desktop snapshot, lists
available applications, and launches each sandboxed app in sequence. Review the console
output to inspect the simulated security, storage, networking, and developer subsystems.

### Windows launcher

A `launcher.bat` script is provided for convenience. Double-clicking it (or running it from `cmd`)
will execute the same demo sequence on Windows and leave the console window open so you can review the
boot log and app output.
