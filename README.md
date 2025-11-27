Memory Interaction Simulator

A small Python project that models how different operations affect multiple memory regions.
Everything is written using the Python standard library — no external packages.

Features

A SystemState with five memory regions (R1–R5)

A collection of operations (E1–E8) that:

mix and transform region data

blend or combine regions

reapply prior changes

or choose an operation at random

A run_script function that:

takes a list of steps

applies each transformation in order

returns the full sequence of system states

Requires only Python 3 (no external libraries)

Example: Running the simulator

Run the file directly:

python engine.py


This will:

create an initial state

run a small scripted sequence of operations

print each resulting state

Example: Using it from another Python script
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
for s in sequence:
    print(s)

Design Notes / FAQ
What type is used for memory regions?

Each region (R1–R5) stores data using Python’s built-in bytes type.

A bytes value is an ordered list of values between 0 and 255. For example:

b""                  # zero-length, no bytes
b"\x00"              # one byte with value 0
b"\x01\xFF\x10"      # three bytes: 1, 255, 16


In this project, each region represents a fixed-size memory block, such as 32 or 64 bytes.
This means:

A region should never be truly empty

A region may contain zero bytes, which is valid data

Example of valid zero-filled memory:

b"\x00" * 32     # 32 actual bytes

Why does mix_bytes reject empty buffers?

mix_bytes is meant to operate on real memory blocks — values that have an actual length.

A zero-length buffer (b"") means:

no bytes exist

nothing can be rotated, XORed, or swapped

this usually indicates a programming mistake

This is not the same as a block of zeros, which is valid.

So the mixer starts with:

if data is None or len(data) == 0:
    raise ValueError("mix_bytes expected a non-empty bytes buffer")


This ensures:

Empty buffers cause a clear error

Real memory blocks (even if all zeros) are transformed normally

Dependencies

Uses only Python standard library modules:

dataclasses

typing

random

os (optional example code only)

No packages to install.

---

## Reference 8-bit system model

This simulator is loosely inspired by a classic 8-bit, tile-based handheld system:

- 8-bit CPU with a small register set and simple instruction set
- banked memory (separate work RAM, video RAM, and save / backup RAM)
- sprite/tile graphics with decompression into working buffers
- game state stored in a compact serialized format, then re-loaded into working memory for rendering and logic

The code in this repository does **not** emulate that hardware directly.  
Instead, it abstracts the idea of “memory regions” and “operations” on them.  

For more detail on the underlying hardware model this is loosely based on (without naming any specific console or game), see:

- `HARDWARE_NOTES.md`
