import json
import os

dataset_name = os.getenv("DATASET_NAME", "world-cities")
input_file = f"dataset/{dataset_name}.json"

with open(input_file, "r", encoding="utf-8") as f:
    cities = json.load(f)

for percent in range(10, 110, 10):
    count = int(len(cities) * (percent / 100))
    part = cities[:count]
    output_file = f"dataset/{dataset_name}_{percent}.json"
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(part, out, ensure_ascii=False, indent=2)