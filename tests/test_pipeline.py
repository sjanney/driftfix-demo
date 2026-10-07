import json

from .helpers import completion
from support_bot.pipeline import handle_new_ticket

TICKET = {"id": "T-7", "order_id": "A1001", "messages": [("customer", "Where is my order A1001?")]}


def replies(client, escalate):
    client.chat.completions.create.side_effect = [
        completion(json.dumps({"category": "shipping", "priority": "normal", "language": "en"})),
        completion(json.dumps({"escalate": escalate, "reason": "routine" if not escalate else "VIP"})),
        completion("- Customer asks where A1001 is"),
        completion("Where is order A1001"),
        completion("Hi! It shipped and arrives Oct 9."),
    ]
    return client


def test_routine_ticket_gets_a_draft(client):
    view = handle_new_ticket(replies(client, False), TICKET)
    assert view["labels"]["category"] == "shipping"
    assert view["draft"] == "Hi! It shipped and arrives Oct 9."
    draft_system = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "status: shipped" in draft_system


def test_escalated_ticket_gets_no_draft(client):
    view = handle_new_ticket(replies(client, True), TICKET)
    assert view["escalate"] and view["draft"] is None
