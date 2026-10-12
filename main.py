
"""Run the provisional QFF C1 H2 VQE development experiment."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

SCRIPTS = [
    ROOT / "src" / "benchmark.py",
    ROOT / "src" / "h2_vqe.py",
]

def main():
    for script in SCRIPTS:
        if not script.is_file():
            raise FileNotFoundError(f"Required script is missing: {script}")

        print(f"\n{'=' * 60}")
        print(f"Running: {script.relative_to(ROOT)}")
        print("=" * 60)

        subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            check=True,
        )

    print("\nPrototype execution completed.")
    print("Inspect results/tables/ and results/figures/.")
    print(
        "Important: these are provisional development results, "
        "not an official noisy Processor A/B benchmark."
    )

if __name__ == "__main__":
    main()
