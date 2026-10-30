"""Pure-numpy checks of the tapering core (no qiskit needed): python -m pytest tests -q"""
import json, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from c1.reduction import taper, hf_to_bits, z_symmetries  # noqa: E402

M = {"I": np.eye(2), "X": np.array([[0, 1], [1, 0]]), "Y": np.array([[0, -1j], [1j, 0]]), "Z": np.diag([1, -1])}


def mat(terms):
    H = 0
    for l, c in terms:
        m = np.array([[1.0]])
        for ch in l:
            m = np.kron(m, M[ch])
        H = H + c * m
    return H


def _load():
    d = json.load(open(os.path.join(ROOT, "data", "c1", "h2_0.735.json")))
    return [(l, c) for l, c in d["operator_jw"]], d["meta"]


def test_two_qubit_taper_matches_fci():
    terms, meta = _load()
    red, kept, eig, hf = taper(terms, 4, [[1, 1, 0, 0], [0, 0, 1, 1]], [1, 3], hf_to_bits(meta["hf_bitstring"]))
    e = np.linalg.eigvalsh(mat(red))[0] + meta["constant_hartree"]
    assert abs(e - meta["e_fci_full_space_hartree"]) < 1e-6
    assert kept == [0, 2] and hf == [1, 1] and len(red) == 5


def test_symmetry_group_dimension():
    terms, _ = _load()
    assert len(z_symmetries(terms, 4)) == 3      # even-weight Z strings: alpha, beta, orbital parity
