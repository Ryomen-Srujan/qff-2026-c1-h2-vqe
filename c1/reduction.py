"""Z2 qubit tapering for PS-C1 (pure-Python core on Pauli-label dicts + SparsePauliOp wrappers).

Conventions: Qiskit labels, qubit 0 is the RIGHT-most character. A Pauli is (x, z, sign) with
x[q], z[q] in {0,1} (Y = x=z=1) and sign in {+1,-1}.
"""
import numpy as np


# ---------- Pauli bookkeeping ----------
def _bits(label):
    n = len(label)
    x = [0] * n
    z = [0] * n
    for q in range(n):
        ch = label[n - 1 - q]
        x[q] = 1 if ch in "XY" else 0
        z[q] = 1 if ch in "ZY" else 0
    return x, z


def _label(x, z):
    out = []
    for q in reversed(range(len(x))):
        out.append("IXZY"[x[q] + 2 * z[q]] if False else {(0, 0): "I", (1, 0): "X", (0, 1): "Z", (1, 1): "Y"}[(x[q], z[q])])
    return "".join(out)


def conjugate_cx(x, z, sign, c, t):
    """Heisenberg conjugation CX(c,t) P CX(c,t) (CX is self-inverse). Aaronson-Gottesman rule."""
    if x[c] & z[t] & (x[t] ^ z[c] ^ 1):
        sign = -sign
    x = list(x)
    z = list(z)
    x[t] ^= x[c]
    z[c] ^= z[t]
    return x, z, sign


# ---------- symmetry search ----------
def z_symmetries(terms, n):
    """All Z-type Z2 symmetries (bit vectors s, Z^s commutes with every term): the GF(2)
    null space of the X-part matrix of the operator. Returns a list of basis vectors."""
    rows = [_bits(lbl)[0] for lbl, _ in terms if any(_bits(lbl)[0])]
    rows = [r[:] for r in {tuple(r) for r in rows}]
    # null space of rows (m x n) over GF(2)
    mat = [r[:] for r in rows]
    piv_cols, r = [], 0
    for col in range(n):
        p = next((i for i in range(r, len(mat)) if mat[i][col]), None)
        if p is None:
            continue
        mat[r], mat[p] = mat[p], mat[r]
        for i in range(len(mat)):
            if i != r and mat[i][col]:
                mat[i] = [a ^ b for a, b in zip(mat[i], mat[r])]
        piv_cols.append(col)
        r += 1
    free = [c for c in range(n) if c not in piv_cols]
    basis = []
    for f in free:
        s = [0] * n
        s[f] = 1
        for i, pc in enumerate(piv_cols):
            if mat[i][f]:
                s[pc] = 1
        basis.append(s)
    return basis


def taper(terms, n, generators, pivots, hf_bits):
    """Taper the qubits `pivots` using the Z-type symmetries `generators` (one pivot each, pivot in
    the support of its generator, and no other pivot in that support), in the sector of `hf_bits`
    (list, hf_bits[q] = value of qubit q).

    Returns (reduced_terms, kept_qubits, sector_eigenvalues, reduced_hf_bits).
    reduced_terms is a list of (label over the kept qubits, coeff); coefficients are real."""
    eig = [(-1) ** (sum(g[q] & hf_bits[q] for q in range(n)) % 2) for g in generators]
    acc = {}
    for lbl, c in terms:
        x, z = _bits(lbl)
        sign = 1
        for g, p in zip(generators, pivots):
            for q in range(n):
                if q != p and g[q]:
                    x, z, sign = conjugate_cx(x, z, sign, q, p)   # CX(control q, target p)
        coef = complex(c) * sign
        for p, e in zip(pivots, eig):
            assert x[p] == 0, "pivot qubit still carries X/Y: not a symmetry of the operator"
            if z[p]:
                coef *= e
        keep = [q for q in range(n) if q not in pivots]
        key = _label([x[q] for q in keep], [z[q] for q in keep])
        acc[key] = acc.get(key, 0) + coef
    kept = [q for q in range(n) if q not in pivots]
    red = [(k, float(np.real(v))) for k, v in acc.items() if abs(v) > 1e-12]
    return red, kept, eig, [hf_bits[q] for q in kept]


def hf_to_bits(hf_label):
    """'0101' (Qiskit label) -> [b_q0, b_q1, ...]"""
    return [int(ch) for ch in reversed(hf_label)]


def bits_to_label(bits):
    return "".join(str(b) for b in reversed(bits))


# ---------- SparsePauliOp wrappers ----------
def taper_operator(op, hf_label, generators, pivots):
    """op: SparsePauliOp (4q JW). Returns (reduced SparsePauliOp, reduced HF label, info dict)."""
    from qiskit.quantum_info import SparsePauliOp
    terms = [(p.to_label(), complex(c)) for p, c in zip(op.paulis, op.coeffs)]
    red, kept, eig, hf_red = taper(terms, op.num_qubits, generators, pivots, hf_to_bits(hf_label))
    rop = SparsePauliOp.from_list(red).simplify()
    return rop, bits_to_label(hf_red), {"kept_qubits": kept, "sector": eig, "pivots": list(pivots)}
