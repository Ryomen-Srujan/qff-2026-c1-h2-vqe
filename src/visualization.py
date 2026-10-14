"""
Plotting utilities for coupling maps, energy convergence, and comparisons.
"""
import matplotlib.pyplot as plt
import networkx as nx
from qiskit.transpiler import CouplingMap


def plot_coupling_map(coupling_map: CouplingMap, title: str,
                      save_path: str = None):
    """Draw the processor coupling graph."""
    G = nx.Graph()
    G.add_edges_from(coupling_map.get_edges())
    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(6, 5))
    nx.draw(G, pos, with_labels=True, node_color="lightblue",
            node_size=600, font_weight="bold", edge_color="gray")
    plt.title(title)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()


def plot_energy_comparison(results_dict: dict, save_path: str = None):
    """Bar chart of VQE energies vs exact across processors."""
    labels = list(results_dict.keys())
    vqe_energies = [results_dict[k]["vqe_energy"] for k in labels]
    exact = results_dict[labels[0]]["exact_energy"]

    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x, vqe_energies, color=["#1f77b4", "#ff7f0e", "#2ca02c"])
    ax.axhline(exact, color="red", linestyle="--", label=f"Exact = {exact:.6f} Ha")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Energy (Hartree)")
    ax.set_title("C1: H₂ Ground-State Energy — Processor Comparison")
    ax.legend()
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()
