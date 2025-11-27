# Memory Interaction Simulator

This project models how different operations affect multiple memory regions in a small system.

- Written in pure Python (standard library only)
- No external or third-party dependencies
- Designed for experimenting with glitch-like or unusual state transitions

## Features

- A `SystemState` structure with five regions (`R1`–`R5`)
- A library of operations (`E1`–`E8`) that:
  - mix and transform data
  - combine multiple regions
  - reapply previous transitions
  - or choose an operation at random
- A `run_script` helper that:
  - takes a list of steps
  - applies each transformation in order
  - returns the full sequence of system states

## Example usage

Running the script directly:

```bash
python engine.py
```

This:
- creates an initial `SystemState`
- runs a short transformation script
- prints each intermediate state

To embed it into another Python file:

```python
from engine import SystemState, Region, run_script

initial = SystemState(
    R1=Region(b"\x00" * 64),
    R2=Region(b"\x00" * 64),
    R3=Region(b"\x00" * 32),
    R4=Region(b"\x00" * 32),
    R5=Region(b"\x00" * 64),
)

steps = [
    {"op": "E1", "ctx": {}},
    {"op": "E5", "ctx": {}},
    {"op": "E6", "ctx": {"source": "R2"}},
]

sequence = run_script(initial, steps)
```

## Implementation notes

- Language: **Python 3**
- Uses only these built-in modules:
  - `dataclasses` (for simple value containers)
  - `typing` (type hints)
  - `random` (for the wildcard operation)
  - `os` (used only in an example block; not required for the core engine)

There are **no external libraries**.

---

# Design notes / FAQ

## What type is used for the memory regions?

Each region (`R1`–`R5`) stores its contents as a Python `bytes` object.

A `bytes` value is an ordered sequence of integers between 0 and 255. Examples:

```python
b""                  # zero-length, no bytes at all
b"\x00"              # one byte, value 0
b"\x01\xFF\x10"      # three bytes: 1, 255, 16
```

In this project, a region represents a **fixed-size memory block** (e.g., 32 or 64 bytes).  
So the system assumes:

- the buffer is **never truly empty**,  
- but may contain **zero bytes**, which is still valid data.

## Why does `mix_bytes` reject empty buffers?

The mixer is designed to operate on real memory blocks.

A zero-length buffer (`b""`) means **no bytes exist at all**, which typically indicates:

- an uninitialized region  
- a missing value  
- or accidental misuse of the API

This is different from a valid block of zeros:

```python
b"\x00" * 32       # 32 bytes of actual data
```

So the mixer explicitly rejects empty buffers:

```python
if data is None or len(data) == 0:
    raise ValueError("mix_bytes expected a non-empty bytes buffer")
```

This guarantees:

- true empties are treated as errors  
- real memory blocks (even if zero-filled) are processed normally

---


