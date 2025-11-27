# Reference 8-bit Hardware Model (Abstract)

This project is loosely inspired by a classic **8-bit handheld system** with:

- a simple 8-bit CPU
- banked memory (work RAM, video RAM, backup/save RAM)
- tile/sprite-based graphics
- compact, serialized game state stored in a save area

No specific console, game, or cryptocurrency is referenced here.  
The notes below exist only to explain the kind of mental model that informed the design of this simulator.

---

## CPU and instruction style (abstract)

The reference system uses:

- an **8-bit accumulator-centric CPU**
- a small set of registers (for example: accumulator, flags, index registers, stack pointer, program counter)
- instruction patterns like:
  - load/store between registers and memory
  - arithmetic/logic (ADD, SUB, AND, OR, XOR)
  - bit shifts/rotations
  - conditional branches and jumps
  - simple stack operations (PUSH/POP)

Example pseudo-assembly (not tied to any specific ISA):

```asm
; Load a value from memory into the accumulator
LD   A, [HL]      ; A <- *(HL)

; XOR with a constant mask
XOR  0x1F         ; A <- A XOR 0x1F

; Store it back
LD   [HL], A      ; *(HL) <- A

; Advance pointer
INC  HL           ; HL <- HL + 1
