"""Drafts email replies and canned macros for agents to review."""

from . import config

TONE = "Warm, concise, no more than 120 words. Sign off as 'The Acme Support Team'."


def draft_reply(client, ticket_text, facts):
    """facts: dict of things the draft may state (order status, refund amount)."""
    fact_lines = "\n".join(f"- {k}: {v}" for k, v in sorted(facts.items()))
    response = client.chat.completions.create(
        model=config.DRAFT_MODEL,
        messages=[
            {"role": "system", "content": f"Draft a reply to the customer. {TONE} Only state these facts:\n{fact_lines}"},
            {"role": "user", "content": ticket_text},
        ],
    )
    return response.choices[0].message.content.strip()


def build_macro(client, topic):
    """A reusable canned response for a common topic, e.g. 'late delivery'."""
    response = client.chat.completions.create(
        model="gpt-4o-2024-05-13",
        messages=[{"role": "user", "content": f"Write a support macro about {topic}. {TONE} Use {{name}} for the customer's name."}],
    )
    return response.choices[0].message.content.strip()
