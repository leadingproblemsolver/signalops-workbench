from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from signalops.core import Action, Store


with tempfile.TemporaryDirectory() as directory:
    store = Store(Path(directory) / "signalops.db")
    store.configure_policy(
        {
            "channel": "reddit",
            "reply_threshold": 6,
            "dm_threshold": 8,
            "call_threshold": 9,
            "dm_requires_response": True,
        }
    )
    surface, decision = store.process(
        channel="reddit",
        title="Wrong root cause",
        url="https://example.com/incidents/1",
        pain="premature conclusion",
        exact_language="We fixed the symptom twice.",
        relevance=9,
        urgency=8,
        conversation=9,
        responded=False,
        who="SRE",
    )
    assert decision.action is Action.PUBLIC_REPLY
    store.record_outcome(surface.external_id, "replied", "Requested a technical example")
    print(
        json.dumps(
            {
                "status": "PASS",
                "decision": decision.to_dict(),
                "events": len(store.events(surface.external_id)),
            },
            indent=2,
        )
    )
