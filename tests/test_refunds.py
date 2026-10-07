from support_bot.refunds import get_refund_status


def test_known_refund():
    assert get_refund_status("r2001")["status"] == "approved"


def test_unknown_refund():
    assert "error" in get_refund_status("R0")
