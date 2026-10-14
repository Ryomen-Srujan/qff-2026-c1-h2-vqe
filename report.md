# C1: H₂ Molecular Ground-State Energy (VQE) — Qiskit Fall Fest 2026

## Problem Statement
**Track:** Quantum Chemistry (VQE / Ab-Initio)  
**Statement:** C1 — Compute the ground-state electronic energy of molecular Hydrogen ($H_2$) at equilibrium ($R = 0.74\text{ \AA}$) using VQE and evaluate architectural trade-offs across controlled hardware topologies.

---

## Benchmark Results

| Architecture | Qubits | Transpiled CX | Depth | Ground Energy (Ha) | Energy Error (mHa) | Chemical Accuracy (<1.6 mHa) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exact (FCI)** | — | — | — | **-1.852388** | **0.0000** | Exact Reference |
| **Ideal (Statevector)** | 4 | 18 | 21 | **-1.851967** | **0.4212** | **✓ YES** |
| **Processor A (5Q Chain)** | 5 | 36 | 76 | **-1.663166** | **189.2219** | ✗ No |
| **Processor B (9Q Sparse)** | 9 | 30 | 58 | **-1.686839** | **165.5491** | ✗ No |
| **Processor D (Custom 4Q)** | 4 | 18 | 33 | **-1.781241** | **71.1467** | ✗ No (62.4% better than A) |

---

## Key Findings
1. **Algorithmic Accuracy:** Our multi-restart VQE achieves **$0.4212\text{ mHa}$ error** in ideal simulation, comfortably surpassing the $1.6\text{ mHa}$ chemical accuracy threshold.
2. **Routing Bottleneck:** On 1D chain hardware (Processor A), SWAP routing causes a **$2\times$ inflation in CX gate count** (18 $\rightarrow$ 36), resulting in severe noise accumulation ($189.22\text{ mHa}$ error).
3. **Co-Design Innovation (Processor D):** Our custom 4-qubit all-to-all topology completely eliminates SWAP overhead, cutting CX count back to 18 and reducing energy error by **$62.4\%$**.

---

## Repository Structure
```text
├── README.md               # Project overview & key results
├── main.ipynb              # Reproducible end-to-end benchmark notebook
├── report.md               # Comprehensive architecture co-design report
├── requirements.txt        # Environment dependencies
├── processors/             # Hardware coupling maps & specs (A, B, D)
│   ├── processor_a.json
│   ├── processor_b.json
│   └── processor_d.json
├── src/                    # Reusable modular codebase
│   ├── problem.py          # H2 Hamiltonian & classical FCI solver
│   ├── processors.py       # Topology loaders & synthetic noise models
│   ├── routing.py          # SABRE transpilation workflows
│   ├── metrics.py          # Circuit depth, CX count & energy metrics
│   └── visualization.py    # Coupling maps & energy plotting routines
└── results/                # Output datasets & generated figures
    ├── circuit_metrics.csv
    ├── energy_comparison.csv
    └── figures/
        ├── coupling_maps.png
        └── energy_comparison.png
