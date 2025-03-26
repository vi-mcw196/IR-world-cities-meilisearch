import os
import time
import json
import meilisearch
import psutil
import requests
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from meilisearch.errors import MeilisearchTimeoutError

# Configuration
MEILISEARCH_HOST = os.getenv("MEILISEARCH_HOST", "http://meilisearch:7700")
DATASET_PATH = "/app/dataset/world-cities.json"
OUTPUT_DIR = "/app/output"
INDEX_NAME = "cities"
BATCH_SIZES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]  # 10% to 100%
PARALLEL_QUERIES = 5

client = meilisearch.Client(MEILISEARCH_HOST)

def load_dataset():
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

def clear_index():
    try:
        client.index(INDEX_NAME).delete()
        time.sleep(1)
    except:
        pass
    client.create_index(INDEX_NAME, {"primaryKey": "geonameid"})

def index_batch(data, fraction):
    batch_size = int(len(data) * fraction)
    batch = data[:batch_size]
    
    start_time = time.time()
    task = client.index(INDEX_NAME).add_documents(batch)
    try:
        client.wait_for_task(task.task_uid, timeout_in_ms=60000, interval_in_ms=1000)
    except MeilisearchTimeoutError:
        print(f"Warning: Indexing task timed out but may still be processing in the background.")
        time.sleep(10)
    
    indexing_time = time.time() - start_time
    
    stats = client.index(INDEX_NAME).get_stats()
    doc_count = stats.number_of_documents
    index_size = stats.raw_document_db_size / 1024 / 1024  # Convert to MB
    
    return {
        "fraction": fraction,
        "doc_count": doc_count,
        "index_size_mb": index_size,
        "indexing_time_s": indexing_time
    }

def measure_resource_usage():
    pid = os.getpid()
    process = psutil.Process(pid)
    cpu_percent = process.cpu_percent(interval=1)
    ram_mb = process.memory_info().rss / 1024 / 1024
    return {"cpu_percent": cpu_percent, "ram_mb": ram_mb}

def measure_response_time(query="Warsaw"):
    def single_query():
        start = time.time()
        response = requests.post(
            f"{MEILISEARCH_HOST}/indexes/{INDEX_NAME}/search",
            json={"q": query},
            headers={"Content-Type": "application/json"}
        )
        return time.time() - start if response.status_code == 200 else float("inf")

    with ThreadPoolExecutor(max_workers=PARALLEL_QUERIES) as executor:
        times = list(executor.map(lambda _: single_query(), range(PARALLEL_QUERIES)))
    return {
        "avg_response_time_s": np.mean(times),
        "min_response_time_s": np.min(times),
        "max_response_time_s": np.max(times)
    }

def analyze_trends(results):
    df = pd.DataFrame(results)
    df["time_per_size"] = df["indexing_time_s"] / df["index_size_mb"]
    
    slope, intercept = np.polyfit(df["index_size_mb"], df["indexing_time_s"], 1)
    linearity = f"indexing_time = {slope:.2f} * index_size + {intercept:.2f}"
    
    return df, linearity

def main():
    Path(OUTPUT_DIR).mkdir(exist_ok=True)
    data = load_dataset()
    total_docs = len(data)
    print(f"Total documents: {total_docs}")
    
    results = []
    for fraction in BATCH_SIZES:
        print(f"Indexing {fraction*100}% of dataset...")
        clear_index()
        stats = index_batch(data, fraction)
        results.append(stats)
        print(f"  Docs: {stats['doc_count']}, Size: {stats['index_size_mb']:.2f} MB, Time: {stats['indexing_time_s']:.2f} s")
    
    df, linearity = analyze_trends(results)
    df.to_csv(f"{OUTPUT_DIR}/indexing_stats.csv", index=False)
    with open(f"{OUTPUT_DIR}/trend_analysis.txt", "w") as f:
        f.write(f"Trend: {linearity}\n")
    print(f"Trend: {linearity}")
    
    print("Monitoring resources...")
    resource_stats = measure_resource_usage()
    response_stats = measure_response_time()
    
    with open(f"{OUTPUT_DIR}/resource_monitoring.json", "w") as f:
        json.dump({**resource_stats, **response_stats}, f, indent=2)
    print(f"CPU: {resource_stats['cpu_percent']}%, RAM: {resource_stats['ram_mb']:.2f} MB")
    print(f"Avg Response Time: {response_stats['avg_response_time_s']:.3f} s")

if __name__ == "__main__":
    main()