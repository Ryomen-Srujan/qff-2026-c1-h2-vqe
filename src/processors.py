"""Load processor configs and build noise models."""
import json
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError


def load_coupling_map(json_path: str):
    """Return (CouplingMap, config_dict)."""
    with open(json_path) as f:
        cfg = json.load(f)
    return CouplingMap(cfg["coupling_map"]), cfg


def build_noise_model(
    sq_depolarizing: float = 0.001,
    cx_depolarizing: float = 0.005,
    readout_bitflip: float = 0.01,
) -> NoiseModel:
    noise = NoiseModel()
    noise.add_all_qubit_quantum_error(
        depolarizing_error(sq_depolarizing, 1), ["rz", "sx", "x"]
    )
    noise.add_all_qubit_quantum_error(
        depolarizing_error(cx_depolarizing, 2), ["cx"]
    )
    noise.add_all_qubit_readout_error(ReadoutError([
        [1 - readout_bitflip, readout_bitflip],
        [readout_bitflip, 1 - readout_bitflip],
    ]))
    return noise
