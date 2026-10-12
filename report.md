# Qiskit Fall Fest 2026 — C1: Molecular Ground-State Energy of H₂

## 1. Project Status

**Status:** Provisional development experiment  
**Problem ID:** C1  
**Track:** Quantum Chemistry  
**Algorithm:** Variational Quantum Eigensolver (VQE)

This report documents the current development prototype and preliminary architecture benchmarks. The results have not yet been validated against the official C1 Hamiltonian, reference energy, or final processor specifications. They must therefore not be interpreted as final challenge results.

## 2. Problem Overview

The objective of C1 is to estimate the ground-state energy of a hydrogen molecule (H₂) using the Variational Quantum Eigensolver.

VQE combines a parameterized quantum circuit with a classical optimization algorithm. The circuit prepares a trial quantum state, and the Hamiltonian expectation value estimates its energy. A classical optimizer then adjusts the circuit parameters to minimize this energy.

The quality of the result depends on the Hamiltonian, the expressiveness of the ansatz, the optimization process, and the quantum circuit resources required by the target architecture.

## 3. Development Environment

The prototype was developed and tested using the following configuration:

| Component | Configuration |
|---|---|
| Python | 3.14.7 |
| Qiskit | 2.5.2 |
| Qiskit Aer | 0.17.2 |
| Classical optimizer | COBYLA |
| Maximum objective evaluations | 500 |
| Transpiler optimization level | 1 |
| Transpiler seed | 42 |
| Simulation method | Ideal statevector |
| Noise model | Not applied |

These settings describe the current development experiment and may differ from the final organizer-required benchmark configuration.

## 4. Methodology

The current prototype follows these steps:

1. Define a provisional two-qubit Hamiltonian for the development experiment.
2. Construct a parameterized quantum circuit.
3. Evaluate the Hamiltonian expectation value using ideal statevector simulation.
4. Optimize the circuit parameters using COBYLA.
5. Record the energy values during optimization to study convergence.
6. Transpile a representative circuit against the current Processor A and Processor B coupling maps.
7. Record circuit depth, CX gate count, and total gate count for preliminary architecture analysis.

The energy optimization and architecture smoke test are separate parts of the current workflow. The smoke test evaluates transpilation and resource metrics; it does not establish that the official H₂ problem has been solved on either processor.

## 5. Preliminary VQE Results

- Final VQE energy: -1.8572731802 Hartree
- Exact matrix ground energy: -1.8572750302 Hartree
- Absolute energy error: 0.0000018500 Hartree
- Optimizer success: True
- Optimizer evaluations: 1201
- Maximum allowed evaluations: 2000
- Optimizer termination: Trust-region radius reached its lower bound
### Interpretation

The reported final energy is lower than the initial energy, indicating that the optimization process reduced the objective value during the experiment.

The small variation across the final ten evaluations suggests that the objective values had stabilized near the end of the run. However, this alone does not establish that the optimizer found the global minimum or that the energy is physically correct for the official H₂ instance.

The reported absolute energy error depends on the reference value used by the script. Since the official Hamiltonian and reference energy have not yet been verified, this error must be treated as provisional rather than as a validated accuracy result.

The optimizer used the maximum configured number of objective evaluations. Further validation is required to determine whether the optimization converged adequately.

## 6. Preliminary Processor A and Processor B Comparison

The current two-qubit circuit produced the following transpilation metrics:

| Metric | Processor A | Processor B |
|---|---:|---:|
| Physical qubits available | 5 | 9 |
| Logical qubits in circuit | 2 | 2 |
| Circuit depth | 10 | 10 |
| CX gates | 2 | 2 |
| Total gates | 18 | 18 |

### Interpretation

The current circuit produced identical reported resource metrics on both processor configurations. This is consistent with a small circuit whose existing two-qubit interactions do not require additional routing under the tested configurations.

However, these results do not demonstrate that the architectures are equivalent in general. A larger circuit, a different qubit layout, or more restrictive connectivity could produce different transpilation results.

No explicit SWAP gates were reported in these current metrics. This does not, by itself, establish the absence of all routing overhead under every layout or transpilation configuration.

The processor definitions used in this experiment remain provisional. A valid final comparison requires the authoritative coupling maps and the same documented benchmark settings on both architectures.

## 7. Simulation Limitations

The current VQE calculation uses ideal statevector simulation. No gate noise, measurement noise, or finite-shot sampling was applied.

Consequently, the current results do not measure the effect of hardware noise, statistical measurement uncertainty, or noisy execution on energy accuracy.

The architecture comparison is also preliminary because it uses a small development circuit and has not yet been validated against the final processor specifications.

## 8. Outstanding Work

The following tasks remain before the experiment can be considered a final C1 submission:

1. Confirm the official H₂ Hamiltonian and reference energy.
2. Validate the Hamiltonian representation and ansatz for the selected instance.
3. Confirm the authoritative Processor A and Processor B coupling maps.
4. Apply the required transpilation, layout, routing, and seed settings.
5. Implement the specified noise model and shot count if required by the final benchmark instructions.
6. Re-run VQE and architecture benchmarks using the confirmed specifications.
7. Compare the resulting energy against a valid exact or classical reference.
8. Export the final convergence plot, resource tables, and coupling-map visualizations.
9. Prepare the required notebook and ensure that all results can be reproduced from the documented environment.

## 9. Conclusion

The current project contains a working VQE development prototype and preliminary processor transpilation benchmarks. The optimization reduced the reported energy from its initial value, while the tested two-qubit circuit produced identical resource metrics on the two current processor configurations.

These findings are useful for validating the development workflow, but they are not yet sufficient to establish the accuracy of the official H₂ ground-state energy calculation or a meaningful performance advantage for either processor.

The next stage is to verify the official problem and processor definitions, execute the required experiments, and replace the provisional measurements with validated results.