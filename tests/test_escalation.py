import json

from .helpers import completion
from support_bot import escalation


def test_escalates_legal_threats(client):
    client.chat.completions.create.return_value = completion(json.dumps({"escalate": True, "reason": "legal threat"}))
    assert escalation.should_escalate(client, "My lawyer will contact you") == (True, "legal threat")


def test_review_refund_reads_the_verdict(client):
    client.chat.completions.create.return_value = completion("APPROVE - within 30 days.")
    ok, why = escalation.review_refund(client, {"amount": 40}, "30-day returns")
    assert ok and why.startswith("APPROVE")
    client.chat.completions.create.return_value = completion("Reject: outside the window.")
    assert escalation.review_refund(client, {"amount": 40}, "30-day returns")[0] is False
