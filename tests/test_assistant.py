import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from support_bot.assistant import reply, start_conversation


def _message_item(text):
    return SimpleNamespace(
        type="message",
        content=[SimpleNamespace(text=SimpleNamespace(value=text))],
    )


def fake_client(answer="Your order shipped.", tool_calls=None):
    client = MagicMock()
    client.conversations.create.return_value = SimpleNamespace(id="conv_1")

    if tool_calls:
        call = SimpleNamespace(
            type="function_call",
            id="call_1",
            call_id="call_1",
            name="get_order_status",
            arguments=json.dumps({"order_id": "a1001"}),
        )
        first_response = SimpleNamespace(
            output=[call],
            output_text=None,
            error=None,
        )
        final_response = SimpleNamespace(
            output=[_message_item(answer)],
            output_text=answer,
            error=None,
        )
        client.responses.create.side_effect = [first_response, final_response]
    else:
        client.responses.create.return_value = SimpleNamespace(
            output=[_message_item(answer)],
            output_text=answer,
            error=None,
        )
    return client


def test_start_conversation_returns_an_id():
    assert start_conversation(fake_client()) == "conv_1"


def test_reply_returns_the_assistant_answer():
    client = fake_client("Hello! How can I help?")
    assert reply(client, "conv_1", "hi", poll_seconds=0) == "Hello! How can I help?"


def test_reply_runs_the_order_tool_and_sends_its_output():
    client = fake_client("Order A1001 shipped.", tool_calls=True)
    assert reply(client, "conv_1", "where is A1001?", poll_seconds=0) == "Order A1001 shipped."
    sent = client.responses.create.call_args_list[1].kwargs["input"]
    tool_outputs = [i for i in sent if isinstance(i, dict) and i.get("type") == "function_call_output"]
    assert json.loads(tool_outputs[0]["output"])["status"] == "shipped"


def test_reply_raises_when_the_run_fails():
    client = fake_client()
    client.responses.create.return_value = SimpleNamespace(
        output=[],
        output_text="",
        error=SimpleNamespace(message="internal error"),
    )
    with pytest.raises(RuntimeError):
        reply(client, "conv_1", "hi", poll_seconds=0)
