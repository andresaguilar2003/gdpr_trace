# gdpr/utils.py

from datetime import datetime

def sort_trace_by_time(trace):
    events = sorted(
        trace,
        key=lambda e: e.get("time:timestamp", datetime.min)
    )
    trace._list = events

def get_first_event_timestamp(trace):
    return min(event["time:timestamp"] for event in trace)
