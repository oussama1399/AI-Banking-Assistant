# AI Banking Assistant - Metrics Dashboard

## How to View Application Metrics

Your AI Banking Assistant automatically collects and exposes metrics at the `/metrics` endpoint. Here are two ways to view them:

### 1. Simple Console Viewer

Run this script to see metrics in your terminal:
```bash
python simple_metrics.py
```

This will show real-time metrics updating every 30 seconds.

### 2. Web-based Dashboard

To use the web dashboard, you'll need to install Streamlit first:
```bash
pip install streamlit
```

Then run:
```bash
streamlit run metrics_dashboard.py
```

This provides a clean, web-based interface to view your application metrics.

## Available Metrics

The metrics include information about:
- Chat requests processed
- HTTP request handling
- Response times
- Error counts
- Application performance

## Accessing Metrics Directly

You can also access metrics directly via curl or any HTTP client:
```bash
curl http://localhost:8000/metrics
```

## Prerequisites

Make sure your AI Banking Assistant application is running before viewing metrics:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```