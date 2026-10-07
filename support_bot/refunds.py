"""Refund lookups the assistant can call as a tool."""

REFUNDS = {
    "R2001": {"order_id": "A1001", "status": "approved", "amount": 42.50},
    "R2002": {"order_id": "A1002", "status": "pending_review", "amount": 129.00},
}


def get_refund_status(refund_id):
    refund = REFUNDS.get(refund_id.upper())
    if refund is None:
        return {"error": f"no refund {refund_id}"}
    return {"refund_id": refund_id.upper(), **refund}
