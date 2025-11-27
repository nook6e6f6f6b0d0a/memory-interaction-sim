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
## Design notes / FAQ

### What type is used for the memory regions?

Each region (`R1`–`R5`) stores its contents as a Python `bytes` object.

A `bytes` value is an ordered sequence of integers between 0 and 255. For example:

```python
b""                  # zero-length, no bytes at all
b"\x00"              # one byte, value 0
b"\x01\xFF\x10"      # three bytes: 1, 255, 16
```

In this project, a region is expected to represent a fixed-size memory block (for example, 32 or 64 bytes long). That means the code assumes the buffer will generally be non-empty and contain actual data, even if some of the bytes are zero.

### Why does `mix_bytes` reject empty buffers?

The `mix_bytes` function is intended to operate on real memory blocks, not on “no data at all”.

A true zero-length `bytes` value (`b""`) is different from a block of zeros (like `b"\x00" * 32`):

- `b""` means there are **no bytes**.
- `b"\x00" * 32` means there are **32 bytes**, each with value 0 — this is still valid memory.

Because the system is modeled around fixed-size regions, an empty buffer usually indicates a bug or an uninitialized value. For that reason, `mix_bytes` contains a check like:

```python
if data is None or len(data) == 0:
    raise ValueError("mix_bytes expected a non-empty bytes buffer")
```

This makes the behavior explicit:

- If the caller passes an empty buffer, the function raises a clear error.
- If the caller passes a non-empty `bytes` block (even if it is all zeros), the function proceeds with the transformation normally.


