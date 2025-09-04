import json
from pathlib import Path
from datetime import datetime


path = Path("data.json")


#збереження iвенту
def save_events(events: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)


def save_event(event: dict):
    events = load_events()  
    if event["name"].startswith("/"):
        return
    events.append(event)
    save_events(events)


#вивод iвентiв
def load_events() -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
        

def load_sorted_events() -> list[dict]:
    events = load_events()
    def parse_date(ev):
        try:
            return datetime.strptime(ev.get("date", "2100-01-01"), "%Y-%m-%d")
        except ValueError:
            return datetime(2100, 1, 1)  # если кривая дата — в конец списка
    events.sort(key=parse_date)
    return events


