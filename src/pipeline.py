import csv
import time
from pathlib import Path
from collections import defaultdict


def extract(input_path):
    """Read penguin records from a CSV file."""
    with open(input_path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def transform(records):
    """Clean, convert, and summarize penguin body mass."""
    groups = defaultdict(list)
    rejected = 0

    for record in records:
        try:
            mass = float(record["body_mass_g"])
            species = record["species"].strip()
            island = record["island"].strip()

            if not species or not island or not 0 < mass < float("inf"):
                raise ValueError("Invalid record")

            mass_kg = mass / 1000
            groups[(species, island)].append(mass_kg)

        except (ValueError, TypeError, KeyError, AttributeError):
            rejected += 1

    summary = []

    for (species, island), masses in sorted(groups.items()):
        summary.append({
            "species": species,
            "island": island,
            "penguin_count": len(masses),
            "average_body_mass_kg": round(sum(masses) / len(masses), 3)
        })

    return summary, rejected


def load(records, output_path):
    """Save summarized records to a CSV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "species",
        "island",
        "penguin_count",
        "average_body_mass_kg"
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


def run_pipeline(input_path, output_path):
    """Execute the complete ETL pipeline and report metrics."""
    start = time.perf_counter()

    records = extract(input_path)
    summary, rejected = transform(records)
    load(summary, output_path)

    elapsed = time.perf_counter() - start

    print("ETL pipeline completed successfully.")
    print(f"Records read: {len(records)}")
    print(f"Records rejected: {rejected}")
    print(f"Records processed: {len(records) - rejected}")
    print(f"Records written: {len(summary)}")
    print(f"Elapsed time: {elapsed:.4f} seconds")
    print(f"Output saved to: {output_path}")

    return summary


if __name__ == "__main__":
    run_pipeline(
        "data/penguins.csv",
        "output/penguin_summary.csv"
    )
