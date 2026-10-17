# C1: H₂ Ground-State Energy — Qiskit Fall Fest 2026

## Problem
Estimate the H₂ ground-state energy near R = 0.74 Å using VQE, then analyze how processor connectivity and noise affect circuit resources and energy error.

## Project contents
- `main.ipynb` — primary end-to-end workflow and saved historical outputs.
- `processors/processor_a.json` — Processor A configuration.
- `processors/processor_b.json` — updated 9-qubit sparse graph (8 undirected edges / 16 directed edges).
- `processors/processor_d.json` — conceptual Processor D design proposal; not part of the Phase 1 A/B execution benchmark.
- `src/` — Hamiltonian, processor, routing, metrics, and visualization helpers.
- `data/h2_distances.json` — H₂ geometry and saved reference-energy metadata.
- `results/` — saved tables and figures.
- `report.md` — architecture analysis, Processor D design rationale, results, and limitations.

## Environment and run
Use a compatible Python environment with the versions in `requirements.txt`. PySCF installation may require a supported Python/platform combination. From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
jupyter lab main.ipynb
```

Run notebook cells from top to bottom. Some archived outputs may reflect an earlier environment; do not treat them as freshly reproduced until the notebook completes successfully and the CSV/figures are regenerated.

## Important reproducibility notes
- The saved reference value is `-1.85238817 Ha`; verify whether the chosen comparison uses electronic energy or total energy including nuclear repulsion.
- Saved A/B metrics show zero explicit SWAP gates. Any claim of routing-added SWAP overhead must be regenerated using a clearly documented metric.
- Processor D uses lower noise probabilities than A/B in the archived configuration. Its saved result is exploratory and is not a controlled topology-only comparison.
- Processor D is retained as a design proposal with rationale; A/B results are reported separately.
- Do not cite historical results as newly reproduced unless the run is successful from a clean environment.

## Results
See `report.md` and `results/energy_comparison.csv`. Values are historical saved outputs and require end-to-end reproduction before final submission.


## Latest preliminary A/B benchmark

The current local run uses the reconstructed four-qubit Hamiltonian in
`data/h2_hamiltonian.json`, a 16-parameter hardware-efficient ansatz, and
4096 shots. Results below are preliminary and are not independently verified
against an organizer-provided Hamiltonian.

| Metric | Processor A | Processor B |
|---|---:|---:|
| Physical qubits | 5 | 9 |
| Logical qubits | 4 | 4 |
| Noisy energy (Ha) | -1.778557 | -1.795586 |
| Absolute error (mHa) | 73.831 | 56.803 |
| Circuit depth | 15 | 15 |
| CX gates | 6 | 6 |
| Explicit SWAP gates | 0 | 0 |
| Shots | 4096 | 4096 |
| Optimizer evaluations | 60 | 60 |
| Chemical accuracy (<= 1.6 mHa) | No | No |

Processor B has the lower observed error in this run, but neither processor
reaches chemical accuracy. These results should be described as preliminary:
the noisy optimizer budget is limited to 60 evaluations, and the Hamiltonian
coefficients were reconstructed from saved notebook output.

The saved CSV is `results/tables/h2_noisy_ab_final.csv`. The legacy notebook
outputs and historical tables may use earlier configurations; do not conflate
them with this latest run.
