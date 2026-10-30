"""Shared C1 setup: locked operators, reduction, Processor D. Everything else imports from here."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "starter"))
from qff_chem import (load_operator, exact_ground_energy, pauli_cost, hf_circuit,  # noqa: E402
                      load_processor, validate_processor_d, PROCESSOR_A, PROCESSOR_B)
from c1.reduction import taper_operator  # noqa: E402

OP_JW, CONST, META = load_operator(os.path.join(ROOT, "data", "c1", "h2_0.735.json"))
E_FCI = META["e_fci_full_space_hartree"]
HF_JW = META["hf_bitstring"]                       # '0101'

# Reduction: Z2 tapering in the HF sector with the alpha-parity (Z0 Z1) and beta-parity (Z2 Z3)
# symmetries; pivots are qubits 1 and 3, qubits 0 and 2 remain.
GEN_ALPHA, GEN_BETA = [1, 1, 0, 0], [0, 0, 1, 1]
OP_RED, HF_RED, RED_INFO = taper_operator(OP_JW, HF_JW, [GEN_ALPHA, GEN_BETA], [1, 3])

OPERATORS = {   # label -> (operator, constant, HF label, method)
    "JW-4q": (OP_JW, CONST, HF_JW, "none"),
    "tapered-2q": (OP_RED, CONST, HF_RED, "Z2 tapering (alpha-parity, beta-parity)"),
}
MAIN_LABEL = "tapered-2q"


def check_reduction(tol=1e-6):
    e = exact_ground_energy(OP_RED, CONST)
    assert abs(e - E_FCI) < tol, f"reduced operator ground energy {e} != E_FCI {E_FCI}"
    return e


def get_processor_D():
    p = load_processor(os.path.join(ROOT, "processors", "processor_D.json"))
    errs = validate_processor_d(p, required_qubits=OP_JW.num_qubits)   # largest required circuit = JW 4q
    if errs:
        raise ValueError("Processor D invalid: " + "; ".join(errs))
    return p
