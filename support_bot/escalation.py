"""Decides when a ticket needs a human lead, and reviews risky refund decisions."""

import json

from . import config

ESCALATE_PROMPT = (
    "Decide whether this support ticket must go to a team lead. Escalate legal threats, "
    'safety issues, and refunds over $500. Reply with JSON: {"escalate": bool, "reason": str}'
)


def should_escalate(client, ticket_text):
    completion = client.chat.completions.create(
        model=config.REASONING_MODEL,
        reasoning_effort="high",
        messages=[{"role": "developer", "content": ESCALATE_PROMPT}, {"role": "user", "content": ticket_text}],
        response_format={"type": "json_object"},
    )
    data = json.loads(completion.choices[0].message.content)
    return bool(data["escalate"]), data.get("reason", "")


def review_refund(client, refund, policy_text):
    """Second opinion on a refund decision before money moves."""
    completion = client.chat.completions.create(
        model="o1",
        messages=[
            {"role": "user", "content": f"Policy:\n{policy_text}\n\nRefund:\n{json.dumps(refund)}\n\n"
             "Does this refund follow the policy? Answer APPROVE or REJECT, then one sentence why."},
        ],
    )
    answer = completion.choices[0].message.content.strip()
    return answer.upper().startswith("APPROVE"), answer
