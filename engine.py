from dataclasses import dataclass
from typing import Dict, Any, List, Callable
import random
import os


# ========= Generic mixing utilities =========

def rotate_left_bits(data: bytes, n: int) -> bytes:
    """Rotate bits left across the entire buffer."""
    if data is None or len(data) == 0:
    raise ValueError("mix_bytes expected a non-empty bytes buffer")
    bit_len = len(data) * 8
    n %= bit_len
    val = int.from_bytes(data, "big")
    val = ((val << n) | (val >> (bit_len - n))) & ((1 << bit_len) - 1)
    return val.to_bytes(len(data), "big")


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """XOR two equal-length byte strings."""
    if len(a) != len(b):
        raise ValueError("xor_bytes: inputs must have same length")
    return bytes(x ^ y for x, y in zip(a, b))


def permute_bytes(data: bytes, key: bytes) -> bytes:
    """
    Deterministic byte permutation based on a key buffer.
    Looks like a generic shuffle routine.
    """
    if not data or not key:
        return data

    indices = list(range(len(data)))
    # Use a small internal mixer for pseudo-random indices
    mixed_key = mix_bytes(key, rounds=2)

    for i in range(len(indices) - 1, 0, -1):
        j = mixed_key[i % len(mixed_key)] % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]

    return bytes(data[i] for i in indices)


def mix_bytes(data: bytes, rounds: int = 3) -> bytes:
    """
    Generic mixing routine:
    - rotates bits in each byte
    - XORs neighbors
    - swaps some pairs
    No external primitives, just simple operations.
    """
       if data is None or len(data) == 0:
        raise ValueError("mix_bytes expected a non-empty bytes buffer")

    buf = bytearray(data)

    for r in range(rounds):
        # Step 1: rotate each byte differently
        for i in range(len(buf)):
            b = buf[i]
            shift = ((i + r) % 7) + 1
            buf[i] = ((b << shift) | (b >> (8 - shift))) & 0xFF

        # Step 2: XOR each byte with its neighbor
        for i in range(len(buf)):
            buf[i] ^= buf[(i + 1) % len(buf)]

        # Step 3: swap some pairs based on a simple rule
        for i in range(0, len(buf) - 1, 2):
            if ((buf[i] + buf[i + 1] + r) & 1) == 0:
                buf[i], buf[i + 1] = buf[i + 1], buf[i]

    return bytes(buf)


# ========= Regions and global state =========

@dataclass
class Region:
    data: bytes

    def copy(self) -> "Region":
        return Region(self.data[:])

    def xor(self, other: "Region") -> "Region":
        return Region(xor_bytes(self.data, other.data))

    def rotate(self, n_bits: int) -> "Region":
        return Region(rotate_left_bits(self.data, n_bits))

    def permute(self, key: bytes) -> "Region":
        return Region(permute_bytes(self.data, key))


@dataclass
class SystemState:
    """
    Abstract memory layout.

    R1, R2, R3, R4, R5:
    - generic buffers/regions whose meaning you define externally.
    """
    R1: Region
    R2: Region
    R3: Region
    R4: Region
    R5: Region

    def copy(self) -> "SystemState":
        return SystemState(
            R1=self.R1.copy(),
            R2=self.R2.copy(),
            R3=self.R3.copy(),
            R4=self.R4.copy(),
            R5=self.R5.copy(),
        )


# ========= Interaction functions (E1–E8) =========

InteractionFn = Callable[[SystemState, Dict[str, Any]], SystemState]


def E1(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E1: Distortion on R1 using R3 + R2 as key material.
    """
    s = state.copy()
    key_material = s.R3.data + s.R2.data
    env_key = mix_bytes(key_material)
    rotated = s.R1.rotate(env_key[0])
    s.R1 = rotated.permute(env_key)
    return s


def E2(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E2: Distortion on first half of R1 using R3 + R4.
    """
    s = state.copy()
    key_material = s.R3.data + s.R4.data
    env_key = mix_bytes(key_material)

    half = len(s.R1.data) // 2
    first = rotate_left_bits(s.R1.data[:half], env_key[1])
    first = permute_bytes(first, env_key)
    s.R1 = Region(first + s.R1.data[half:])
    return s


def E3(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E3: Distortion on R1 using R3 + R4 + R5 with a stronger global scramble.
    """
    s = state.copy()
    key_material = s.R3.data + s.R4.data + s.R5.data
    env_key = mix_bytes(key_material, rounds=4)

    rotated = s.R1.rotate(env_key[2])
    pad = (env_key * (len(rotated.data) // len(env_key) + 1))[:len(rotated.data)]
    xored = xor_bytes(rotated.data, pad)
    s.R1 = Region(permute_bytes(xored, env_key[::-1]))
    return s


def E4A(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E4A: Setup event.
    Uses R1 + R4 to populate R2 and adjust R3.
    """
    s = state.copy()
    frozen = mix_bytes(s.R1.data + s.R4.data)

    rep = (frozen * (len(s.R2.data) // len(frozen) + 1))[:len(s.R2.data)]
    s.R2 = Region(rep)

    # Perturb R3 with part of the mixed buffer
    n = min(len(s.R3.data), len(frozen))
    new_R3 = xor_bytes(s.R3.data[:n], frozen[:n])
    if n < len(s.R3.data):
        new_R3 += s.R3.data[n:]
    s.R3 = Region(new_R3)

    return s


def E4B(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E4B: Resolve event.
    Uses R2 + R3 to modify R1 and R4.
    """
    s = state.copy()
    key = mix_bytes(s.R2.data + s.R3.data)

    pad = (key * (len(s.R1.data) // len(key) + 1))[:len(s.R1.data)]
    s.R1 = Region(xor_bytes(s.R1.data, pad))

    flag_pad = mix_bytes(key + b"flags")
    flag_pad_full = (flag_pad * (len(s.R4.data) // len(flag_pad) + 1))[:len(s.R4.data)]
    s.R4 = Region(xor_bytes(s.R4.data, flag_pad_full))

    return s


def E5(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E5: Copy/merge-style interaction between R2 and R3.
    """
    s = state.copy()
    half = len(s.R3.data) // 2
    combined = s.R2.data[:half] + s.R3.data[half:]
    combined = combined[:len(s.R3.data)]
    s.R3 = Region(combined)
    return s


def E6(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E6: Blend interaction.
    Context may specify source region name ('R1', 'R2', 'R4', 'R5').
    """
    s = state.copy()
    src_name = ctx.get("source", "R1")
    src_region: Region = getattr(s, src_name)

    n = min(len(s.R3.data), len(src_region.data))
    blended = xor_bytes(s.R3.data[:n], src_region.data[:n])
    if n < len(s.R3.data):
        blended += s.R3.data[n:]
    s.R3 = Region(blended)
    return s


def E7(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E7: Echo interaction.
    Reapplies the previous delta to a target region (default R1).
    """
    s = state.copy()
    prev_delta = ctx.get("prev_delta", b"\x00" * len(s.R1.data))
    target_name = ctx.get("target", "R1")

    region: Region = getattr(s, target_name)
    new_data = xor_bytes(region.data, prev_delta[:len(region.data)])
    setattr(s, target_name, Region(new_data))
    return s


def E8(state: SystemState, ctx: Dict[str, Any]) -> SystemState:
    """
    E8: Wildcard interaction.
    Picks another interaction from a pool and applies it.
    """
    s = state.copy()
    pool: List[InteractionFn] = ctx.get("pool", [])
    if not pool:
        return s
    chosen = random.choice(pool)
    return chosen(s, ctx)


# ========= Registry and script runner =========

OPS: Dict[str, InteractionFn] = {
    "E1": E1,
    "E2": E2,
    "E3": E3,
    "E4A": E4A,
    "E4B": E4B,
    "E5": E5,
    "E6": E6,
    "E7": E7,
    "E8": E8,
}


def run_script(initial: SystemState, steps: List[Dict[str, Any]]) -> List[SystemState]:
    """
    steps: list of {"op": <"E1"..."E8">, "ctx": {...}}
    Returns the sequence of states (including initial).
    Tracks previous R1 delta for echo-style steps.
    """
    sequence = [initial]
    prev_state = initial
    prev_delta = b"\x00" * len(initial.R1.data)

    for step in steps:
        op_name = step["op"]
        ctx = dict(step.get("ctx", {}))
        ctx.setdefault("prev_delta", prev_delta)

        fn = OPS[op_name]
        new_state = fn(prev_state, ctx)

        prev_delta = xor_bytes(prev_state.R1.data, new_state.R1.data)
        sequence.append(new_state)
        prev_state = new_state

    return sequence


# ========= Tiny demo (optional) =========

if __name__ == "__main__":
    # Example initial state with fixed sizes.
    init = SystemState(
        R1=Region(b"\x00" * 64),
        R2=Region(b"\x00" * 64),
        R3=Region(os.urandom(32)),
        R4=Region(b"\x00" * 32),
        R5=Region(b"\x00" * 64),
    )

    steps = [
        {"op": "E4A", "ctx": {}},
        {"op": "E1", "ctx": {}},
        {"op": "E7", "ctx": {"target": "R1"}},
        {"op": "E6", "ctx": {"source": "R5"}},
        {"op": "E8", "ctx": {"pool": [E2, E3, E5]}},
        {"op": "E4B", "ctx": {}},
    ]

    seq = run_script(init, steps)
    for i, s in enumerate(seq):
        print(f"--- State {i} ---")
        print("R1:", s.R1.data.hex())
        print("R2:", s.R2.data.hex())
        print("R3:", s.R3.data.hex())
        print("R4:", s.R4.data.hex())
        print("R5:", s.R5.data.hex())
        print()
