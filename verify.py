import os
import json
import sqlite3
import requests
import hashlib
import logging
from datetime import datetime
import sys
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/verify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_and_print(message, level="info"):
    print(message)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
def check_files(files):
    results = {}
    for f in files:
        if os.path.exists(f):
            results[f] = "PASS"
            log_and_print(f"File check passed for {f}")
        else:
            results[f] = "FAIL"
            log_and_print(f"File check failed for {f}", "error")
    return results
def check_database(db_config):
    try:
        conn = sqlite3.connect(db_config["path"])
        cursor = conn.cursor()
        results = {}
        for table, columns in db_config["tables"].items():
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [row[1] for row in cursor.fetchall()]
                missing = [c for c in columns if c not in cols]
                if missing:
                    results[table] = f"FAIL (missing columns: {missing})"
                    log_and_print(f"Database check failed: {table} missing {missing}", "error")
                else:
                    results[table] = "PASS"
                    log_and_print(f"Database check passed for table {table}")
            except sqlite3.Error as e:
                results[table] = f"FAIL ({str(e)})"
                log_and_print(f"Database error on {table}: {e}", "error")
        conn.close()
        return results
    except Exception as e:
        log_and_print(f"Database connection failed: {e}", "error")
        return {"database": f"FAIL ({str(e)})"}
def check_api(endpoints):
    results = {}
    for url in endpoints:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                results[url] = "PASS"
                log_and_print(f"API check passed for {url}")
            else:
                results[url] = f"FAIL (status {r.status_code})"
                log_and_print(f"API check failed for {url}: status {r.status_code}", "error")
        except Exception as e:
            results[url] = f"FAIL ({str(e)})"
            log_and_print(f"API error for {url}: {e}", "error")
    return results
def generate_manifest(files):
    manifest = {}
    for f in files:
        if os.path.exists(f):
            sha256_hash = hashlib.sha256()
            with open(f, "rb") as file:
                for byte_block in iter(lambda: file.read(4096), b""):
                    sha256_hash.update(byte_block)
            manifest[f] = sha256_hash.hexdigest()
            log_and_print(f"Manifest hash generated for {f}")
        else:
            manifest[f] = "MISSING"
            log_and_print(f"Manifest file missing: {f}", "error")

    with open("manifest.json", "w") as mf:
        json.dump(manifest, mf, indent=4)
    return manifest
def main(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    print("\n[Verification Results]")
    file_results = check_files(config.get("files", []))
    for f, res in file_results.items():
        print(f"File: {f} -> {res}")
    db_results = check_database(config.get("database", {}))
    for t, res in db_results.items():
        print(f"Database: {t} -> {res}")
    api_results = check_api(config.get("apis", []))
    for url, res in api_results.items():
        print(f"API: {url} -> {res}")
    manifest = generate_manifest(config.get("manifest", []))
    print("Manifest generated -> manifest.json")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify.py config.json")
    else:
        main(sys.argv[1])
