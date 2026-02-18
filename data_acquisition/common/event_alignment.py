import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timedelta


CONFIG = Path("data_acquisition/config/event_calendar.yaml")


class EventAlignment:

    def __init__(self):
        with open(CONFIG) as f:
            self.events = yaml.safe_load(f)

    def align(self, query: Dict[str, Any]) -> Dict[str, Any] | None:
        """
        Returns event-centered time window if event present.
        """

        event_context = query.get("event_context")

        if not event_context:
            return None

        event_type = event_context.get("event_type")
        relation = event_context.get("temporal_relation", "after")

        if event_type not in self.events:
            return None

        date_str = self.events[event_type][-1] #type: ignore
        event_date = datetime.fromisoformat(date_str)

        if relation == "before":
            return {
                "start": (event_date - timedelta(days=90)).date().isoformat(),
                "end": event_date.date().isoformat()
            }

        return {
            "start": event_date.date().isoformat(),
            "end": (event_date + timedelta(days=90)).date().isoformat()
        }