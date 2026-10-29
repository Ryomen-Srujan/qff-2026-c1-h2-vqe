# QFF 2026 Phase 2 — Quantum Chemistry Challenge Kit

Read **QFF2026_Phase2_Chemistry_Problem_Statements.docx** first. It is the authoritative description of every task, rule, definition and deadline. This kit holds every input it refers to; nothing else needs to be downloaded or requested.

| When (IST) | What |
|---|---|
| Day 1, 6:00 PM | Hackathon starts (help desk for clarifications 6:00–8:00 PM) |
| **Day 2, 5:40 PM** | **Final commit; repository URL submitted on the hackathon portal** (https://qffsrmap2026.com/learning/hackathon) |

## Setup (dedicated environment for this track)

```bash
python3 -m venv chem-env && source chem-env/bin/activate      # Python 3.11, 3.12 or 3.13
pip install --upgrade pip && pip install -r requirements.txt
cd starter && jupyter notebook starter_chem.ipynb               # runs in about 1 minute
```
`requirements-optional.txt` (qiskit-nature, pyscf) is only needed if you want qiskit-nature ansätze such as UCCSD or want to re-derive operators. pyscf has no Windows wheels (use WSL).

## Contents

| Path | What it is |
|---|---|
| `data/instances_index.json` | Every locked value: grids, active spaces, fit windows, reduced masses, constants, processors, settings |
| `data/c1/` | PS-C1: H₂ at R = 0.735 Å — 4-qubit Jordan–Wigner operator (`.json`) + integrals (`.npz`) |
| `data/c2/h2/` | PS-C2: H₂ at 12 bond lengths 0.50–3.00 Å (operator + integrals each) |
| `data/c2/lih/` | PS-C2 advanced tier: LiH at 12 bond lengths 1.00–4.00 Å — 6-qubit active-space operator **and** 4-qubit tapered operator |
| `data/c3/` | PS-C3: H₂O (4e,4o) — 8-qubit active-space operator + integrals |
| `starter/qff_chem.py` | Official settings, Processors A/B, noise model, resource metrics, Bell experiment, Processor D checker, energy estimators (statevector and shot-based with standard error), SPSA, PES helpers |
| `starter/starter_chem.ipynb` | Worked example of the measurement workflow |
| `starter/processor_D_template.json` | Processor D file format |
| `tools/check_processor_d.py` | Copy `starter/processor_D_template.json` to `processors/processor_D.json` in your repository, edit it, then run `python tools/check_processor_d.py processors/processor_D.json <qubits_needed>` from the kit root. Self-test on the template: `python tools/check_processor_d.py starter/processor_D_template.json 4` |
| `templates/results_columns.md` | Required result tables (CSV names and columns) |
| `MANIFEST.sha256` | Checksums of every file |

Each operator `.json` has `meta` (geometry, active space, HF bitstring, `constant_hartree`, `e_hf_hartree`, `e_fci_full_space_hartree`) and `operator_jw` as `[pauli_label, coefficient]` pairs. **Total energy = ⟨ψ|H|ψ⟩ + constant_hartree.** Spin-orbital order: qubits 0…n−1 are α orbitals, n…2n−1 are β (qiskit-nature block order). Integrals `.npz`: `h1`, `h2_chemist` (chemists' notation (pq|rs)), `e_core`, `n_alpha`, `n_beta`.

Answer keys are **not** in this kit.
