"""Order lookups the assistant can call as a tool."""

ORDERS = {
    "A1001": {"status": "shipped", "eta": "2026-10-09"},
    "A1002": {"status": "processing", "eta": "2026-10-14"},
}


def get_order_status(order_id):
    order = ORDERS.get(order_id.upper())
    if order is None:
        return {"error": f"no order {order_id}"}
    return {"order_id": order_id.upper(), **order}
