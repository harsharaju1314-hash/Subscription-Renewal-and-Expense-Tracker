import os
import sys
import time

# Set clean testing environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "super-secret-test-key-minimum-32-chars-long"
os.environ["ENVIRONMENT"] = "testing"
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["CACHE_ENABLED"] = "true"

import pytest

def main():
    print("=" * 70, flush=True)
    print("Running Production Test Suite (FastAPI + Flask AI + FAISS + MILP)", flush=True)
    print("=" * 70, flush=True)

    args = [
        "-v",
        "-p", "no:langsmith_plugin",
        "-p", "no:flask",
        "--tb=short",
        "tests",
    ]

    t0 = time.time()
    retcode = pytest.main(args)
    duration = time.time() - t0

    print("=" * 70, flush=True)
    print(f"Test run completed in {duration:.2f}s with exit code {retcode}", flush=True)
    print("=" * 70, flush=True)

    sys.exit(retcode)

if __name__ == "__main__":
    main()
