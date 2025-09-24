# Ragnar Mini OS

This repository contains a Python-based "mini operating system" simulation. It demonstrates how separate
components can be organised to represent different responsibilities, such as managing the user interfaces,
applications, an automatic update pipeline, boot-time integrity checks, and an all-in-one controller tying
the pieces together.

### Features

* Boot sequence that validates critical files against an integrity manifest before loading services.
* Automatic application catalogue that keeps built-in apps up to date.
* A suite of functional demo applications (notes, calculator, weather, news, system monitor, and more).

Run the demo with:

```bash
python main.py --demo
```
