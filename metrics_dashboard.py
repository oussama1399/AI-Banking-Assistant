"""
Simple Web-based Metrics Dashboard for AI Banking Assistant
This provides a clear interface to view application metrics.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

# Set page configuration
st.set_page_config(
    page_title="AI Banking Assistant - Metrics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("📊 AI Banking Assistant - Metrics Dashboard")
st.markdown("""
This dashboard shows real-time metrics from your AI Banking Assistant.
The metrics are collected automatically by the application and updated every 30 seconds.
""")

# Initialize session state for metrics
if 'metrics' not in st.session_state:
    st.session_state.metrics = {}
    st.session_state.last_updated = None

def fetch_metrics():
    """Fetch metrics from the application"""
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            # Parse the metrics (they're in Prometheus format)
            metrics_data = response.text
            st.session_state.metrics = parse_metrics(metrics_data)
            st.session_state.last_updated = datetime.now()
            return True
    except Exception as e:
        st.error(f"Failed to fetch metrics: {e}")
        return False

def parse_metrics(metrics_text):
    """Parse Prometheus-style metrics"""
    metrics = {}

    # Simple parser for basic metrics
    lines = metrics_text.strip().split('\n')

    for line in lines:
        if line.startswith('#') or not line:
            continue

        # Parse metric name and value
        if ' ' in line:
            parts = line.split(' ', 1)
            metric_name = parts[0]
            metric_value = parts[1]

            # Try to parse as number
            try:
                if '.' in metric_value:
                    metrics[metric_name] = float(metric_value)
                else:
                    metrics[metric_name] = int(metric_value)
            except ValueError:
                metrics[metric_name] = metric_value

    return metrics

def display_metrics():
    """Display the parsed metrics in a clear format"""
    st.subheader("📋 Current Metrics")

    if not st.session_state.metrics:
        st.info("No metrics available. Please ensure the application is running.")
        return

    # Display last updated time
    if st.session_state.last_updated:
        st.caption(f"Last updated: {st.session_state.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")

    # Group metrics by category
    chat_metrics = {}
    request_metrics = {}
    error_metrics = {}
    other_metrics = {}

    for metric_name, value in st.session_state.metrics.items():
        if 'chat' in metric_name.lower() or 'response' in metric_name.lower():
            chat_metrics[metric_name] = value
        elif 'request' in metric_name.lower() or 'http' in metric_name.lower():
            request_metrics[metric_name] = value
        elif 'error' in metric_name.lower() or 'failure' in metric_name.lower():
            error_metrics[metric_name] = value
        else:
            other_metrics[metric_name] = value

    # Display each category
    if chat_metrics:
        st.markdown("### Chat Requests")
        for name, value in chat_metrics.items():
            st.metric(label=name.replace('_', ' ').title(), value=value)

    if request_metrics:
        st.markdown("### HTTP Requests")
        for name, value in request_metrics.items():
            st.metric(label=name.replace('_', ' ').title(), value=value)

    if error_metrics:
        st.markdown("### Errors & Failures")
        for name, value in error_metrics.items():
            st.metric(label=name.replace('_', ' ').title(), value=value)

    if other_metrics:
        st.markdown("### Other Metrics")
        for name, value in other_metrics.items():
            st.metric(label=name.replace('_', ' ').title(), value=value)

def main():
    """Main dashboard function"""

    # Auto-refresh every 30 seconds
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 30)

    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        fetch_metrics()

    # Fetch initial metrics
    if not st.session_state.metrics:
        fetch_metrics()

    # Display metrics
    display_metrics()

    # Auto-refresh loop (this is a bit tricky in Streamlit, so we'll just show the interval)
    st.info(f"Dashboard will automatically refresh every {refresh_interval} seconds")

if __name__ == "__main__":
    main()