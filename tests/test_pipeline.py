import csv

from src.pipeline import extract, transform, load, run_pipeline


def create_sample(path):
    """Create a fixed sample dataset for repeatable tests."""
    path.write_text(
        "species,island,body_mass_g\n"
        "Adelie,Dream,3000\n"
        "Adelie,Dream,4000\n"
        "Gentoo,Biscoe,5000\n"
        "Adelie,Dream,NA\n",
        encoding="utf-8"
    )
    return path


def test_extraction(tmp_path):
    """Verify that the expected records and fields are extracted."""
    input_path = create_sample(tmp_path / "sample.csv")
    records = extract(input_path)

    assert len(records) == 4
    assert records[0]["species"] == "Adelie"
    assert records[0]["island"] == "Dream"
    assert records[0]["body_mass_g"] == "3000"


def test_transformation():
    """Verify unit conversion and average body mass."""
    records = [
        {"species": "Adelie", "island": "Dream", "body_mass_g": "3000"},
        {"species": "Adelie", "island": "Dream", "body_mass_g": "4000"}
    ]

    summary, rejected = transform(records)

    assert rejected == 0
    assert len(summary) == 1
    assert summary[0]["penguin_count"] == 2
    assert summary[0]["average_body_mass_kg"] == 3.5


def test_invalid_or_missing_data():
    """Verify that invalid and missing masses are rejected."""
    records = [
        {"species": "Adelie", "island": "Dream", "body_mass_g": "NA"},
        {"species": "Adelie", "island": "Dream", "body_mass_g": ""},
        {"species": "Adelie", "island": "Dream", "body_mass_g": "-100"},
        {"species": "Adelie", "island": "Dream", "body_mass_g": "3500"}
    ]

    summary, rejected = transform(records)

    assert rejected == 3
    assert len(summary) == 1
    assert summary[0]["penguin_count"] == 1
    assert summary[0]["average_body_mass_kg"] == 3.5


def test_loading(tmp_path):
    """Verify that the saved CSV contains the correct fields and values."""
    output_path = tmp_path / "output.csv"

    records = [{
        "species": "Adelie",
        "island": "Dream",
        "penguin_count": 2,
        "average_body_mass_kg": 3.5
    }]

    load(records, output_path)

    assert output_path.exists()

    with open(output_path, newline="", encoding="utf-8") as file:
        saved = list(csv.DictReader(file))

    assert saved == [{
        "species": "Adelie",
        "island": "Dream",
        "penguin_count": "2",
        "average_body_mass_kg": "3.5"
    }]


def test_complete_pipeline(tmp_path):
    """Verify the expected output from the complete ETL pipeline."""
    input_path = create_sample(tmp_path / "sample.csv")
    output_path = tmp_path / "summary.csv"

    result = run_pipeline(input_path, output_path)

    expected = [
        {
            "species": "Adelie",
            "island": "Dream",
            "penguin_count": 2,
            "average_body_mass_kg": 3.5
        },
        {
            "species": "Gentoo",
            "island": "Biscoe",
            "penguin_count": 1,
            "average_body_mass_kg": 5.0
        }
    ]

    assert result == expected
    assert output_path.exists()

    with open(output_path, newline="", encoding="utf-8") as file:
        saved = list(csv.DictReader(file))

    assert saved == [
        {key: str(value) for key, value in row.items()}
        for row in expected
    ]
