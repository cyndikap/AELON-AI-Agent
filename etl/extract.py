import csv, json, os

def extract_csv(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def extract_json(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def extract_all(raw_dir: str = "data/raw") -> list:
    records = []
    for fname in os.listdir(raw_dir):
        fpath = os.path.join(raw_dir, fname)
        if fname.endswith(".csv"):
            records.extend(extract_csv(fpath))
        elif fname.endswith(".json"):
            records.extend(extract_json(fpath))
    return records
