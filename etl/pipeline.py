from dotenv import load_dotenv
load_dotenv()

from etl.extract import extract_all
from etl.transform import transform
from etl.load import load_to_json, load_to_chroma, load_to_delta

def run_pipeline(raw_dir: str = "data/raw", skip_chroma: bool = False) -> dict:
    raw   = extract_all(raw_dir)
    clean = transform(raw)
    load_to_json(clean)

    indexed = 0
    if not skip_chroma:
        try:
            indexed = load_to_chroma(clean)
        except Exception as e:
            print(f"⚠️  Chroma skipped: {e}")

    return {"extracted": len(raw), "transformed": len(clean), "indexed_in_chroma": indexed}

if __name__ == "__main__":
    result = run_pipeline()
    print(result)
