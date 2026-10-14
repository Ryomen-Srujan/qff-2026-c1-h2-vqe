# Qiskit Fall Fest 2026 — Phase 1: Problem Statement C1
## Molecular Ground-State Energy ($H_2$) via VQE: Algorithm-Architecture Co-Design

---

## 1. Team Information
* **Team Name:** StrawHats
* **Track:** Track A — Quantum Chemistry Track (VQE / Ab-Initio)
* **Problem Statement:** C1 — Molecular Ground-State Energy ($H_2$)

| # | Member Name | GitHub / Contact | Role / Contribution |

## 1. Team Information
* **Team Name:** StrawHats
* **Track:** Track A — Quantum Chemistry Track (VQE / Ab-Initio)
* **Problem Statement:** C1 — Molecular Ground-State Energy (H_2)

| # | Member Name | Role / Contribution |
| :---: | :--- | :--- |
| 1 | **Srujan** (Team Lead) | Project coordination & VQE algorithm implementation |
| 2 | **Bharadwaj** | PySCF Hamiltonian pipeline & chemistry mapping |
| 3 | **Swaroop** | Processor A/B noise benchmarking & transpilation |
| 4 | **Dinesh** | SABRE routing analysis & circuit metrics |
| 5 | **Nithin** | Processor D custom architecture design |
| 6 | **Cherith** | Visualization, report & documentation |---

## 2. Problem Overview & Methodology

### 2.1 Problem Statement
The objective of Problem Statement **C1** is to compute the ground-state electronic energy of the Hydrogen molecule ($H_2$) at equilibrium bond length ($R = 0.74\text{ \AA}$) using the Variational Quantum Eigensolver (VQE), validate against exact classical diagonalization, and evaluate execution performance across controlled hardware processor topologies.

### 2.2 Quantum Chemistry Pipeline
* **Molecular Geometry:** Diatomic Hydrogen ($H_2$) at $R = 0.74\text{ \AA}$ in the STO-3G minimal basis.
* **Qubit Mapping:** Jordan-Wigner transformation mapping 4 molecular spin-orbitals to a 4-qubit Hamiltonian consisting of 15 Pauli terms.
* **Classical Exact Diagonalization (FCI):** $E_0 = -1.85238817\text{ Hartree}$.
* **Chemical Accuracy Threshold:** $\pm 1.6\text{ mHa}$ ($\approx 1\text{ kcal/mol}$).

### 2.3 Algorithm & Variational Ansatz
* **Ansatz:** `efficient_su2` with parameterized $R_y$ and $R_z$ single-qubit rotations, full entanglement layers, and 3 repetitions ($d = 21$ untranspiled depth, 18 CX gates, 32 parameters).
* **Classical Optimizer:** Constrained Optimization by Linear Approximation (`COBYLA`) with multi-restart initialization (5 restarts, up to 1000 iterations each).
* **Simulation Backend:** Qiskit Aer density matrix simulator evaluating 4096 shots under fixed synthetic device noise.

---

## 3. Processor & Architecture Assumptions

All quantum circuits are transpiled using Qiskit's `transpile` with `optimization_level=1`, SABRE layout/routing, and deterministic seed `42` across the basis gates `{rz, sx, x, cx}`.

* **Processor A (5-Qubit Chain):** Historical baseline featuring a nearest-neighbor chain topology with bidirectional edges `(0,1), (1,2), (1,3), (3,4)`.
* **Processor B (9-Qubit Heavy-Hex):** Contemporary execution target with sparse coupling edges `(0,1), (1,2), (1,6), (2,3), (2,6), (2,5), (3,4), (4,5), (5,6), (6,7), (6,8), (8,0)`.
* **Processor C (13-Qubit):** Reserved strictly for architectural study (no execution required in Phase 1).
* **Processor D (4-Qubit Custom Ring):** Custom user-designed all-to-all topology created to eliminate multi-hop SWAP routing overhead for chemistry ansatzes.

### Fixed Synthetic Noise Parameters (Processors A & B):
* Single-qubit depolarizing error ($p_{1Q}$): `0.001`
* Two-qubit CX depolarizing error ($p_{CX}$): `0.005`
* Symmetric readout bit-flip probability ($p_{readout}$): `0.01`

---

## 4. Key Benchmark Results

| Architecture / Platform | Physical Qubits | Transpiled Depth | CX Gate Count | SWAP Overhead | Measured Energy (Ha) | Energy Error (mHa) | Chemical Accuracy (<1.6 mHa) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Exact Classical (FCI)** | — | — | — | — | **-1.852388** | **0.0000** | Exact Reference |
| **Ideal Statevector (Noiseless)** | 4 | 21 | 18 | 0 | **-1.851967** | **0.4212** | **✓ YES** |
| **Processor A (5Q Chain)** | 5 | 76 | 36 | 6 | **-1.663166** | **189.2219** | ✗ No |
| **Processor B (9Q Sparse)** | 9 | 58 | 30 | 4 | **-1.686839** | **165.5491** | ✗ No |
| **Processor D (Custom 4Q Ring)** | 4 | 33 | 18 | 0 | **-1.781241** | **71.1467** | ✗ No (**62.4% error reduction vs A**) |

### Core Insights:
1. **Algorithmic Validation:** Under ideal conditions, our VQE converges to **$0.4212\text{ mHa}$ error**, well within the strict $1.6\text{ mHa}$ chemical accuracy limit.
2. **The Routing Bottleneck:** On 1D linear topologies (Processor A), non-local orbital interactions force SABRE to insert SWAP networks, **doubling CX gate counts from 18 to 36** and increasing error to $189.22\text{ mHa}$.
3. **Co-Design Innovation:** Processor D completely removes the 18 routing-induced CX gates, keeping depth low and recovering **$62.4\%$ of lost energy precision** under device noise.

---

## 5. Repository Structure

```text
.
├── README.md                     # Project overview, methodology, setup & summary
├── report.md                     # In-depth architectural trade-off & co-design report
├── requirements.txt              # Pinned Python package dependencies
├── main.ipynb                    # Fully reproducible end-to-end benchmark notebook
├── data/
│   └── h2_distances.json         # Molecular bond length and reference energy data
├── processors/                   # Hardware architecture coupling maps & definitions
│   ├── processor_a.json          # 5-qubit chain topology configuration
│   ├── processor_b.json          # 9-qubit sparse heavy-hex topology configuration
│   └── processor_d.json          # Custom 4-qubit all-to-all topology configuration
├── src/                          # Reusable modular source code
│   ├── __init__.py
│   ├── problem.py                # H2 electronic Hamiltonian & PySCF driver mapping
│   ├── processors.py             # JSON coupling loaders & Aer noise model builders
│   ├── routing.py                # Deterministic SABRE transpilation workflows
│   ├── metrics.py                # DAG circuit metrics & energy error calculators
│   └── visualization.py          # Network graph & energy benchmark plotting routines
└── results/                      # Output tables and publication figures
    ├── circuit_metrics.csv       # Transpiled gate counts, depth & qubit metrics
    ├── energy_comparison.csv     # Final numerical energies and errors across platforms
    └── figures/
        ├── coupling_maps.png     # Side-by-side topology graphs (A, B, D)
        └── energy_comparison.png # Zoomed energy & error (mHa) comparison charts
