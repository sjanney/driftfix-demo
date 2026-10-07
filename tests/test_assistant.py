import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from support_bot.assistant import reply, start_conversation


def fake_client(answer="Your order shipped.", first_status="completed", tool_call=None):
    client = MagicMock()
    client.conversations.create.return_value = SimpleNamespace(id="conv_1")
    first = SimpleNamespace(
        id="run_1",
        status=first_status,
        output=[tool_call] if tool_call else [],
        output_text=answer,
    )
    if tool_call:
        second = SimpleNamespace(
            id="run_2",
            status="completed",
            output=[],
            output_text=answer,
        )
        client.responses.create.side_effect = [first, second]
    else:
        client.responses.create.return_value = first
    return client


def test_start_conversation_returns_an_id():
    assert start_conversation(fake_client()) == "conv_1"


def test_reply_returns_the_assistant_answer():
    client = fake_client("Hello! How can I help?")
    assert reply(client, "conv_1", "hi", poll_seconds=0) == "Hello! How can I help?"


def test_reply_runs_the_order_tool_and_sends_its_output():
    call = SimpleNamespace(
        type="function_call",
        id="fc_1",
        call_id="call_1",
        name="get_order_status",
        arguments=json.dumps({"order_id": "a1001"}),
    )
    client = fake_client("Order A1001 shipped.", first_status="requires_action", tool_call=call)
    assert reply(client, "conv_1", "where is A1001?", poll_seconds=0) == "Order A1001 shipped."
    sent = client.responses.create.call_args_list[1].kwargs["input"]
    assert sent[0]["type"] == "function_call_output"
    assert sent[0]["call_id"] == "call_1"
    assert json.loads(sent[0]["output"])["status"] == "shipped"


def test_reply_raises_when_the_run_fails():
    with pytest.raises(RuntimeError):
        reply(fake_client(first_status="failed"), "conv_1", "hi", poll_seconds=0)
