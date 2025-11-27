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

A run_script helper that applies a sequence of transformations and returns all intermediate states

No dependencies beyond Python 3

Example: Running the simulator

You can run the file directly:

python engine.py


This will:

create an initial state

run a short scripted set of operations

print each resulting state

Example: Using it in your own Python code
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

A bytes value is an ordered sequence of numbers from 0 to 255. Examples:

b""                  # zero-length, no bytes at all
b"\x00"              # one byte with value 0
b"\x01\xFF\x10"      # three bytes: 1, 255, 16


In this project, each region represents a fixed-size memory block, such as 32 or 64 bytes.
That means:

A region should never be truly empty

A region may contain zero values, which is still valid data

Example of a valid zero-filled block:

b"\x00" * 32     # 32 actual bytes

Why does mix_bytes reject empty buffers?

The mix_bytes function is written to operate on real memory blocks.

A zero-length buffer (b"") means:

there are no bytes at all

nothing can be rotated, XORed, swapped, etc.

this usually indicates a programming mistake or uninitialized data

This is different from a block of zeros, which is still real data.

To enforce this distinction, the mixer begins with:

if data is None or len(data) == 0:
    raise ValueError("mix_bytes expected a non-empty bytes buffer")


This ensures:

Invalid empties trigger a clear error

Actual memory blocks (even if zero-filled) are transformed correctly

Dependencies

Only Python's standard library is used:

dataclasses

typing

random

os (optional, used only in an example)

No installation required — just Python 3.

License

MIT License
