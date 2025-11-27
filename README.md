# Memory Interaction Simulator

This project models how different operations affect multiple memory regions in a small system.

- Written in pure Python (standard library only).
- No external dependencies.
- Designed for experimenting with glitch-like or unusual state transitions.
## Features

- Models a small system with multiple memory regions (R1–R5).
- Provides a set of operations (E1–E8) that apply different kinds of transformations:
  - distortions,
  - copy/merge behavior,
  - blend/echo interactions,
  - and a basic “wildcard” operation that chooses an effect at random.
- Includes a simple script runner that takes a list of steps and produces the full sequence of states.

## Implementation details

- Language: Python 3
- Dependencies: **standard library only**
  - `dataclasses` for lightweight data containers
  - `typing` for type hints
  - `random` for the wildcard interaction
  - `os` only in the small demo block to generate an example buffer (not required for core logic)

There are **no external or third-party libraries** involved.

## Example usage

Run the demo directly:

```bash
python engine.py
