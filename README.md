# QFF 2026 Phase 2 — Quantum Chemistry Challenge Kit

## PS-C1: H₂ Ground-State Energy — Hybrid Integration



Read **QFF2026_Phase2_Chemistry_Problem_Statements.docx** first. It is the authoritative description of every task, rule, definition, and deadline. This kit holds every input it refers to; nothing else needs to be downloaded or requested.



| When (IST) | What |

|---|---|

| Day 1, 6:00 PM | Hackathon starts (help desk for clarifications 6:00–8:00 PM) |

| **Day 2, 5:40 PM** | **Final commit; repository URL submitted on the hackathon portal** (https://qffsrmap2026.com/learning/hackathon) |



## 1. Official Challenge Kit



### Setup



```bash

python3 -m venv chem-env \&\& source chem-env/bin/activate

pip install --upgrade pip \&\& pip install -r requirements.txt

cd starter \&\& jupyter notebook starter_chem.ipynb

```



Use Python 3.11, 3.12, or 3.13.



`requirements-optional.txt` (qiskit-nature, pyscf) is only needed if you want Qiskit Nature ansätze such as UCCSD or want to re-derive operators. PySCF has no Windows wheels (use WSL).



### Challenge Kit Contents



| Path | What it is |

|---|---|

| `data/instances_index.json` | Every locked value: grids, active spaces, fit windows, reduced masses, constants, processors, settings |

| `data/c1/` | PS-C1: H₂ at R = 0.735 Å — 4-qubit Jordan–Wigner operator (`.json`) and integrals (`.npz`) |

| `data/c2/h2/` | PS-C2: H₂ at 12 bond lengths from 0.50–3.00 Å (operator and integrals for each) |

| `data/c2/lih/` | PS-C2 advanced tier: LiH at 12 bond lengths from 1.00–4.00 Å — 6-qubit active-space operator and 4-qubit tapered operator |

| `data/c3/` | PS-C3: H₂O (4e,4o) — 8-qubit active-space operator and integrals |

| `starter/qff_chem.py` | Official settings, Processors A/B, noise model, resource metrics, Bell experiment, Processor D checker, energy estimators, SPSA, and PES helpers |

| `starter/starter_chem.ipynb` | Worked example of the measurement workflow |

| `starter/processor_D_template.json` | Processor D file format |

| `tools/check_processor_d.py` | Processor D validation script |

| `templates/results_columns.md` | Required result tables (CSV names and columns) |

| `MANIFEST.sha256` | Checksums of every file |



Each operator `.json` has `meta` (geometry, active space, HF bitstring, `constant_hartree`, `e_hf_hartree`, `e_fci_full_space_hartree`) and `operator_jw` as `\[pauli_label, coefficient]` pairs.



**Total energy:**



\\\[

E_{\\mathrm{total}}=\\langle\\psi|H|\\psi\\rangle+\\text{constant\\_hartree}

\\]



Spin-orbital order: qubits 0…n−1 are α orbitals, and n…2n−1 are β orbitals (Qiskit Nature block order). Integrals `.npz`: `h1`, `h2_chemist` (chemists' notation (pq|rs)), `e_core`, `n_alpha`, `n_beta`.



Answer keys are **not** in this kit.



---



# 2. PS-C1 Project Overview



This project implements and evaluates a hybrid quantum workflow for estimating the ground-state energy of molecular hydrogen (H₂) at a bond length of **0.735 Å** using the **STO-3G** basis.



The exact Full Configuration Interaction (FCI) reference energy used in the integrated analysis is:



`-1.1373060357534004 Ha`



The workflow includes:



- Fermion-to-qubit mapping

- Symmetry reduction and two-qubit tapering

- Variational Quantum Eigensolver (VQE) optimization

- Finite-shot energy estimation

- Bell-pair diagnostics

- Circuit-resource analysis



## 3. Repository Contents



| Path | What it is |

|---|---|

| `c1/` | C1 modules for reduction, setup, VQE sweeps, shot studies, Bell experiments, and resource analysis |

| `c1_pipeline.ipynb` | Integrated C1 analysis notebook |

| `tests/test_reduction.py` | Symmetry-reduction validation tests |

| `processors/processor_D.json` | Processor D topology and noise configuration |

| `results/tables/` | Mapping, sweep, shot, Bell, and resource result tables |

| `results/figures/` | Generated convergence figures |

| `results/best_run_c1.json` | Selected integrated VQE configuration and parameter vector |

| `archive/member3_reference/` | Preserved Member 3 scripts, original report, and historical outputs |



The original starter assets and Phase 1 notebook are retained separately. The archived Member 3 report is preserved unchanged.



## 4. Environment and Reproduction



Run the following commands from the repository root using the configured Python environment:



```powershell

python -m pytest tests -q

python tools/check_processor_d.py processors/processor_D.json 4

python -m jupyter nbconvert --to notebook --execute c1_pipeline.ipynb --output c1_pipeline_executed.ipynb

```



### Recorded Validation Outcomes



- Pytest: **2 passed**.

- Processor D structural check: **OK — Processor D satisfies all design rules**.

- Integrated notebook: executed without cell errors and saved as a separate executed notebook.



The notebook execution command creates `c1_pipeline_executed.ipynb`; it does not overwrite the original source notebook.



## 5. Mapping and Symmetry Reduction



| Representation | Qubits | Non-identity Pauli terms | QWC groups | CX gates on Processor D |

|---|---:|---:|---:|---:|

| Jordan–Wigner (JW-4q) | 4 | 14 | 5 | 3 |

| Symmetry-tapered (tapered-2q) | 2 | 4 | 2 | 1 |



Both representations reproduce the FCI reference energy in the integrated mapping results.



The tapered representation reduces the problem to two qubits while reducing the number of non-identity Pauli terms and qubit-wise commuting (QWC) measurement groups.



## 6. Integrated Hybrid VQE Sweep



The integrated sweep contains 12 configurations:



- Hardware-efficient ansatz depths 1 and 2.

- COBYLA and SPSA optimizers.

- Seeds 0, 1, and 2.



### Best Integrated Result



| Parameter | Result |

|---|---:|

| Mapping | tapered-2q |

| Ansatz depth | 2 |

| Optimizer | COBYLA |

| Seed | 1 |

| Energy | -1.137306035656347 Ha |

| Absolute error | 9.705347636668193 × 10⁻⁸ Ha |

| Optimizer calls | 61 |



The complete sweep is stored in `results/tables/c1_sweep.csv`.



The selected configuration and parameter vector are stored in `results/best_run_c1.json`.



The additional JW-4q sweep is recorded separately in `results/tables/c1_sweep_extra_JW4q.csv`.



## 7. Member 3 Independent Depth-1 Reproduction



The preserved Member 3 `run_best_params.py` was independently executed.



It uses:



- Parity mapping with two-qubit tapering.

- Two-qubit hardware-efficient ansatz with one repetition.

- Hartree–Fock initial state.

- COBYLA optimizer.

- Seed 0.



### Recorded Result



| Quantity | Value |

|---|---:|

| VQE energy | -1.1373060357533036 Ha |

| FCI reference | -1.1373060357534004 Ha |

| Optimizer calls | 99 |

| Ansatz depth | 1 |

| Number of parameters | 4 |



This is a separate depth-1 experiment, not the integrated depth-2 best run.



The four parameters from this experiment must not be used with the integrated depth-2 ansatz, which has six parameters.



## 8. Finite-Shot Energy Estimates



The current integrated shot results are stored in `results/tables/c1_shots.csv`.



There are two QWC measurement groups, so total circuit shots equal twice the shots-per-group value.



| Noise setting | Shots per group | Energy (Ha) | Standard error (Ha) | Signed error (mHa) |

|---|---:|---:|---:|---:|

| Ideal | 1,024 | -1.1412479014 | 0.00823015 | -3.9419 |

| Ideal | 8,192 | -1.1423153592 | 0.00273532 | -5.0093 |

| Processor D noise model | 1,024 | -1.1111502474 | 0.00948116 | +26.1558 |

| Processor D noise model
