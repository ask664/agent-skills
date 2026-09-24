import argparse
import json
from pathlib import Path


def retrieve(product_id):
    path = Path(__file__).resolve().parents[1] / "assets" / "catalog.json"
    records = json.loads(path.read_text())
    return next((item for item in records if item["id"] == product_id), None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("product_id")
    args = parser.parse_args()
    record = retrieve(args.product_id)
    print(json.dumps({"found": record is not None, "product": record}))
