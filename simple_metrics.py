"""
Simple Metrics Viewer for AI Banking Assistant
"""

import requests
import json
from datetime import datetime
import time

def get_metrics():
    """Fetch and display metrics from the application"""
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            print("=== AI BANKING ASSISTANT METRICS ===")
            print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            print("Raw metrics data:")
            print(response.text)
            return True
        else:
            print(f"Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Failed to fetch metrics: {e}")
        print("Make sure the application is running at http://localhost:8000")
        return False

def main():
    """Main function"""
    print("AI Banking Assistant Metrics Viewer")
    print("=" * 40)

    while True:
        print()
        get_metrics()
        print()
        print("Press Ctrl+C to exit")
        try:
            time.sleep(30)  # Refresh every 30 seconds
        except KeyboardInterrupt:
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()