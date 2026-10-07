import json

from .helpers import completion
from support_bot import triage


def test_classify(client):
    client.chat.completions.create.return_value = completion(json.dumps({"category": "refund", "priority": "high", "language": "en"}))
    assert triage.classify(client, "I want my money back")["category"] == "refund"
    assert client.chat.completions.create.call_count == 1


def test_unknown_label_retries_once_on_the_fallback_model(client):
    client.chat.completions.create.side_effect = [
        completion(json.dumps({"category": "complaint", "priority": "high"})),
        completion(json.dumps({"category": "other", "priority": "normal", "language": "de"})),
    ]
    assert triage.classify(client, "Hallo")["language"] == "de"
    first, second = [c.kwargs["model"] for c in client.chat.completions.create.call_args_list]
    assert first != second
