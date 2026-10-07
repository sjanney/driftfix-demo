"""What happens to a new ticket: triage, escalation check, summary and a draft reply."""

from . import drafts, escalation, summarizer, triage
from .orders import get_order_status


def handle_new_ticket(client, ticket):
    """ticket: {"id", "messages": [(author, text)], "order_id"?}. Returns the agent view."""
    first = ticket["messages"][0][1]
    labels = triage.classify(client, first)
    escalate, reason = escalation.should_escalate(client, first)
    facts = {}
    if ticket.get("order_id"):
        facts.update(get_order_status(ticket["order_id"]))
    return {
        "id": ticket["id"],
        "labels": labels,
        "escalate": escalate,
        "escalation_reason": reason,
        "summary": summarizer.summarize_ticket(client, ticket["messages"]),
        "subject": summarizer.headline(client, ticket["messages"]),
        "draft": None if escalate else drafts.draft_reply(client, first, facts),
    }
