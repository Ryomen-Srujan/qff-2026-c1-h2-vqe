# QFF 2026 — C1 H2 VQE Development Log

## Status
Provisional development experiment only.
Not the official QFF benchmark.

## Problem
C1 — Molecular Ground-State Energy (H2)
Track: Quantum Chemistry
Algorithm: Variational Quantum Eigensolver (VQE)

## Development setup
- Python 3.14.7
- Qiskit 2.5.2
- Qiskit Aer 0.17.2
- Optimizer: COBYLA
- Maximum objective evaluations: 500
- Transpiler optimization level: 1
- Transpiler seed: 42
- Noise model: Not applied

## Preliminary energy results
- Initial energy: -1.0973424854 Hartree
- Final VQE energy: -1.8572688581 Hartree
- Reported absolute energy error: 0.0000061721 Hartree
- Objective evaluations: 500
- Range across final 10 evaluations: approximately 9.23e-8 Hartree

## Preliminary architecture results
Processor A:
- Physical qubits: 5
- Circuit depth: 10
- CX gates: 2
- Total gates: 18

Processor B:
- Physical qubits: 9
- Circuit depth: 10
- CX gates: 2
- Total gates: 18

## Interpretation
The ideal two-qubit development circuit produced identical reported
architecture metrics on both processors. This circuit does not yet
demonstrate a difference in routing overhead or noisy performance.

## Outstanding requirements
1. Verify the official C1 Hamiltonian and reference energy.
2. Obtain the final organizer-approved Processor A/B settings.
3. Apply the required noise model, if specified.
4. Verify the required transpiler and routing configuration.
5. Re-run the official benchmark and replace provisional results.
6. Confirm that the final submission meets all organizer requirements.
