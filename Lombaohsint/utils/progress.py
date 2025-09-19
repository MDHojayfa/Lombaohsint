import time
from tqdm import tqdm
import sys

def show_spinner(message):
    """
    Displays a spinning animation while waiting for async operations.
    """
    spinner = ['|', '/', '-', '\\']
    for i in range(10):
        sys.stdout.write(f"\r[{''.join(spinner[i % 4])}] {message}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")  # Clear line

def progress_bar(iterations, delay=0.1, desc="Processing"):
    """
    Displays a progress bar using tqdm.
    Used during long-running API calls or scans.
    """
    for _ in tqdm(range(iterations), desc=desc, ncols=80, leave=False, bar_format='{l_bar}{bar}|'):
        time.sleep(delay)
