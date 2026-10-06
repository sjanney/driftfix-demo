from support_bot.orders import get_order_status


def test_known_order():
    assert get_order_status("a1002")["status"] == "processing"


def test_unknown_order():
    assert "error" in get_order_status("Z9")
