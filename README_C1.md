# PS-C1: H₂ Ground-State Energy — Hybrid Integration

## 1. Project Overview

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

## 2. Repository Contents

- `c1/` — C1 modules for reduction, setup, VQE sweeps, shot studies, Bell experiments, and resource analysis.
- `c1_pipeline.ipynb` — integrated C1 analysis notebook.
- `tests/test_reduction.py` — symmetry-reduction validation tests.
- `processors/processor_D.json` — Processor D topology and noise configuration.
- `results/tables/` — mapping, sweep, shot, Bell, and resource result tables.
- `results/figures/` — generated convergence figures.
- `results/best_run_c1.json` — selected integrated VQE configuration and parameter vector.
- `archive/member3_reference/` — preserved Member 3 scripts, original report, and historical outputs.

The original starter assets and Phase 1 notebook are retained separately. The archived Member 3 report is preserved unchanged.

## 3. Environment and Reproduction

Run the following commands from the repository root using the configured Python environment:

```powershell
python -m pytest tests -q
python tools/check_processor_d.py processors/processor_D.json 4
python -m jupyter nbconvert --to notebook --execute c1_pipeline.ipynb --output c1_pipeline_executed.ipynb
```

Recorded validation outcomes:

- Pytest: **2 passed**.
- Processor D structural check: **OK — Processor D satisfies all design rules**.
- Integrated notebook: executed without cell errors and saved as a separate executed notebook.

The notebook execution command creates `c1_pipeline_executed.ipynb`; it does not overwrite the original source notebook.

## 4. Mapping and Symmetry Reduction

| Representation | Qubits | Non-identity Pauli terms | QWC groups | CX gates on Processor D |
|---|---:|---:|---:|---:|
| Jordan–Wigner (JW-4q) | 4 | 14 | 5 | 3 |
| Symmetry-tapered (tapered-2q) | 2 | 4 | 2 | 1 |

Both representations reproduce the FCI reference energy in the integrated mapping results.

The tapered representation reduces the problem to two qubits while reducing the number of non-identity Pauli terms and qubit-wise commuting (QWC) measurement groups.

## 5. Integrated Hybrid VQE Sweep

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

## 6. Member 3 Independent Depth-1 Reproduction

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

## 7. Finite-Shot Energy Estimates

The current integrated shot results are stored in `results/tables/c1_shots.csv`.

There are two QWC measurement groups, so total circuit shots equal twice the shots-per-group value.

| Noise setting | Shots per group | Energy (Ha) | Standard error (Ha) | Signed error (mHa) |
|---|---:|---:|---:|---:|
| Ideal | 1,024 | -1.1412479014 | 0.00823015 | -3.9419 |
| Ideal | 8,192 | -1.1423153592 | 0.00273532 | -5.0093 |
| Processor D noise model | 1,024 | -1.1111502474 | 0.00948116 | +26.1558 |
| Processor D noise model | 8,192 | -1.1078733994 | 0.00330220 | +29.4326 |

Signed error is the estimated energy minus the FCI reference. A negative value means the estimate is below the reference; a positive value means it is above.

These are simulated finite-shot results, not measurements from a physical quantum processor.

## 8. Bell-Pair Diagnostics

The Bell study compares:

- Qubit pair 0–1: graph distance 1.
- Qubit pair 1–3: graph distance 2.

Both pairs have unit fidelity in the ideal simulation.

Under the configured noise model:

- Near-pair fidelity: approximately 0.9633.
- Farther-pair fidelity: approximately 0.9557.

The fidelity calculation used in the archived analysis is:

`F = (1 + XX - YY + ZZ) / 4`

These values are simulator diagnostics under the selected model. They should not be interpreted as experimental hardware measurements or generalized beyond the simulated configuration.

## 9. Processor D Configuration

Processor D has four qubits and coupling edges:

`(0,1), (1,2), (2,3), (3,0), (0,2)`

Configured native gates:

`rz`, `sx`, `x`, `cx`

Configured error parameters:

- Single-qubit error: 0.001
- Two-qubit error: 0.005
- Readout error: 0.01

The structural validation script passes.

Qubit pair (1,3) is not directly coupled and has graph distance 2. The structural check does not model calibration quality or crosstalk.

## 10. Circuit-Resource Comparison

| Circuit | Logical qubits | CX gates | Depth | Two-qubit depth |
|---|---:|---:|---:|---:|
| JW-4q HEA depth 1 | 4 | 3 | 16 | 3 |
| JW-4q HEA depth 2 | 4 | 6 | 24 | 5 |
| tapered-2q HEA depth 1 | 2 | 1 | 9 | 1 |
| tapered-2q HEA depth 2 | 2 | 2 | 14 | 2 |

The tested variants report zero inserted SWAP gates on the supplied Processor A, B, and D configurations.

These metrics apply only to the tested circuits and transpilation settings. They do not establish that the processor configurations behave identically in general.

## 11. Member 3 Archived Files and Provenance

The `archive/member3_reference/` directory preserves the separately supplied Member 3 study.

Contents include:

- `report.pdf` — original Member 3 report, retained unchanged.
- `make_report_pdf.py` — report-generation script.
- `run_best_params.py` — independent depth-1 VQE reproduction.
- `run_c1_sweep.py` — Member 3 sweep runner.
- `run_c1_shots.py` — Member 3 shot-study runner.
- `run_bell.py` — Bell-pair experiment runner.
- `run_resources.py` — circuit-resource analysis runner.
- `results/c1_best_parameters.npy` — Member 3 parameter artifact.
- `results/tables/c1_convergence_history.csv` — historical convergence trajectories.

To rerun the preserved depth-1 reproduction from the repository root:

```powershell
python archive\member3_reference\run_best_params.py
```

### Archived Report Discrepancy

The archived report's page 2 mapping CX counts conflict with its later resource table and with the current integrated mapping CSV.

The current integrated mapping CSV reports:

- JW-4q: 3 CX gates on Processor D.
- Tapered-2q: 1 CX gate on Processor D.

The archived PDF is intentionally preserved without modification.

Current integrated CSV files should be used when describing the hybrid results. Historical Member 3 values should be identified separately.

## 12. AI Assistance Disclosure

The team used an AI assistant as a supplementary learning and clarification tool, particularly while working through questions about the Bell-state experiment.

The assistance focused on clarifying the Bell-state circuit, the interpretation of two-qubit correlation measurements (XX, YY, and ZZ), and how these correlations contribute to the Bell-state fidelity estimate.

The AI assistant was used for conceptual guidance and troubleshooting. The Bell-state simulations were executed by the team in the project environment, and the reported numerical values were taken from the team's generated result files.

The team reviewed the outputs and remains responsible for the implementation, validation, interpretation, and conclusions presented in the project.

If AI assistance was also used to generate or modify code or other project components, that additional use should be disclosed accurately.

## 13. Limitations

- Processor noise and Bell-pair results are simulated; no physical quantum hardware execution is claimed.
- The chemistry benchmark is limited to H₂ at one bond length and one basis set.
- Finite-shot estimates fluctuate with sampling and may fall above or below the exact reference.
- Resource metrics depend on the ansatz, transpiler settings, and supplied coupling maps.
- The archived Member 3 report contains a mapping-count inconsistency; current integrated CSVs are used for the hybrid results.

## 14. Conclusion

The symmetry-tapered two-qubit formulation reduces the H₂ representation and measurement workload while preserving the FCI reference energy in the mapping validation.

The best integrated depth-2 VQE run reaches an absolute error of approximately 9.71 × 10⁻⁸ Ha in 61 optimizer calls.

The finite-shot, noise-model, Bell-pair, and resource studies provide additional simulated diagnostics for this H₂ benchmark.
