"""Classifies every inbound ticket: category, priority, language."""

import json

from . import config

CATEGORIES = ["shipping", "refund", "billing", "account", "bug", "other"]
PRIORITIES = ["low", "normal", "high", "urgent"]

PROMPT = (
    "Classify this support ticket. Reply with JSON: "
    '{"category": one of %s, "priority": one of %s, "language": ISO 639-1 code}' % (CATEGORIES, PRIORITIES)
)


def classify(client, ticket_text):
    try:
        return _classify(client, config.TRIAGE_MODEL, ticket_text)
    except ValueError:
        # The small model occasionally returns an unknown label; one retry on the fallback model.
        return _classify(client, config.CHEAP_MODEL, ticket_text)


def _classify(client, model, ticket_text):
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": ticket_text}],
        response_format={"type": "json_object"},
    )
    data = json.loads(completion.choices[0].message.content)
    if data.get("category") not in CATEGORIES or data.get("priority") not in PRIORITIES:
        raise ValueError(f"unexpected labels: {data}")
    return data
