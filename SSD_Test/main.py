# main.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "scripts"))

from h2test_auto import run_h2test

if __name__ == "__main__":
    run_h2test(log_file="h2test.log")