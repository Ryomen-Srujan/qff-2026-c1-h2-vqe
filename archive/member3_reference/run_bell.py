
import sys
import csv
from pathlib import Path

sys.path.insert(0, "starter")
import qff_chem as qc

# Load our validated Processor D
processor = qc.load_processor("processors/processor_D.json")

# Near pair and farthest pair
pairs = [(0, 1), (1, 3)]

results = []

# Run ideal and noisy experiments for both pairs
for pair in pairs:
    for noisy in [False, True]:
        result = qc.bell_experiment(
            processor,
            pair,
            noisy=noisy,
            shots=4096
        )

        results.append(result)
        print(result)

# Save all results to CSV
Path("results/tables").mkdir(parents=True, exist_ok=True)

columns = [
    "processor", "pair", "noisy", "shots", "pair_distance",
    "XX", "XX_se", "YY", "YY_se", "ZZ", "ZZ_se",
    "fidelity", "fidelity_se", "cx"
]

with open("results/tables/bell.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    writer.writerows(results)

print("\nBell experiment completed!")
print("Saved to results/tables/bell.csv")
