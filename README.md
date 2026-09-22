# MPC
A Python toolkit for counting AND gates, multiplicative complexity, and circuit depth in MPC-friendly cryptographic primitives (AES S-box, LowMC S-box).
# MPC_counter

A lightweight Python toolkit for **profiling the multiplicative complexity** of MPC-friendly cryptographic primitives.

In secure multi-party computation (MPC), only **AND gates** carry a communication cost — XOR gates are "free". This tool counts AND gates, multiplicative depth, and round complexity so you can compare circuit designs without running a full MPC protocol.

---

## What It Measures

| Metric | Meaning |
|---|---|
| `and_count` | Total AND gates consumed (= total multiplicative cost) |
| `mul_count` | Alias for `and_count` |
| `depth` | Maximum AND-gate depth across all rounds (critical path) |
| `rounds` | Total number of `add_and` calls |

> **Why does depth matter?**  
> In protocols like GMW or SPDZ, each layer of AND gates requires one round of communication. Lower depth → fewer rounds → faster wall-clock time, even if `and_count` stays the same.

---

## Supported Primitives

### AES S-box (`aes_sbox_mpc`)
An 8-bit → 8-bit substitution box implemented as a degree-2 Boolean circuit.  
Uses **23 AND gates** per S-box call (t1–t23; t24–t28 are commented out as a reduced variant under exploration).

**Full encryption:** `aes_encrypt(state, mpc, rounds=14)`  
- Input: 16-byte list  
- Counts AND gates and depth across all 14 rounds; depth resets between rounds via `reset_depth()`

### LowMC S-box (`lowmc_sbox_mpc`)
A 3-bit → 3-bit S-box used in the LowMC block cipher, designed explicitly for MPC.  
Uses **3 AND gates** per S-box call — the minimum for a non-linear 3-bit permutation.

**Full encryption:** `lowmc_encrypt(state_bits, mpc, rounds=30)`  
- Input: flat bit list  
- Processes all 3-bit S-box instances per round

---

## Quick Start

```python
from AND import MPCCounter, aes_encrypt, lowmc_encrypt

# --- AES ---
mpc = MPCCounter()
state = [
    0x32, 0x43, 0xF6, 0xA8,
    0x88, 0x5A, 0x30, 0x8D,
    0x31, 0x31, 0x98, 0xA2,
    0xE0, 0x37, 0x07, 0x34
]
out = aes_encrypt(state, mpc, rounds=14)
print("AND count:", mpc.and_count)   # 16 bytes × 23 AND/S-box × 14 rounds = 5152
print("Max depth:", mpc.depth)

# --- LowMC ---
mpc = MPCCounter()
state_bits = [0, 1, 0, 1, ...]      # flat bit list (length must be divisible by 3)
out = lowmc_encrypt(state_bits, mpc, rounds=30)
print("AND count:", mpc.and_count)
print("Max depth:", mpc.depth)
```

---

## File Structure

```
MPC_counter/
├── AND.py          # Core counter + AES S-box + LowMC S-box implementations
└── README.md
```

---

## Known Issues / Work in Progress

- **`aes_sbox_mpc`**: Line 72 (`y7 = ...`) has an indentation error in the current source — fix by aligning it with `y6` above.
- **LowMC `state_bits`**: A missing comma on line 176 (`1,0,1,0,1,1,0,0` → should end with `,`) causes a silent integer concatenation bug.
- The commented-out `t24`–`t28` terms represent a **full quadratic expansion** variant of the AES S-box (28 AND gates). The active code uses a **reduced 23-AND variant** — the trade-off between the two is the subject of ongoing exploration.

---

## Background

| Cipher | S-box AND gates | AND depth | MPC friendliness |
|---|---|---|---|
| AES | 23 (this impl.) / 32 (naive) | up to 4 | Moderate |
| LowMC | 3 | 1 | High (designed for MPC) |

LowMC was co-designed by Albrecht, Rechberger et al. specifically to minimize AND gates for post-quantum signature schemes (e.g. Picnic). AES requires far more AND gates but benefits from hardware acceleration in other contexts.

---

## License

MIT
