import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from support_bot.assistant import reply, start_conversation


def text_message(value):
    return SimpleNamespace(content=[SimpleNamespace(text=SimpleNamespace(value=value))])


def fake_client(answer="Your order shipped.", first_status="completed", tool_call=None):
    client = MagicMock()
    client.beta.threads.create.return_value = SimpleNamespace(id="thread_1")
    first = SimpleNamespace(id="run_1", status=first_status, required_action=None)
    if tool_call:
        first.required_action = SimpleNamespace(
            submit_tool_outputs=SimpleNamespace(tool_calls=[tool_call])
        )
    client.beta.threads.runs.create.return_value = first
    client.beta.threads.runs.submit_tool_outputs.return_value = SimpleNamespace(
        id="run_1", status="completed"
    )
    client.beta.threads.messages.list.return_value = SimpleNamespace(data=[text_message(answer)])
    return client


def test_start_conversation_returns_an_id():
    assert start_conversation(fake_client()) == "thread_1"


def test_reply_returns_the_assistant_answer():
    client = fake_client("Hello! How can I help?")
    assert reply(client, "thread_1", "hi", poll_seconds=0) == "Hello! How can I help?"


def test_reply_runs_the_order_tool_and_sends_its_output():
    call = SimpleNamespace(
        id="call_1",
        function=SimpleNamespace(name="get_order_status", arguments=json.dumps({"order_id": "a1001"})),
    )
    client = fake_client("Order A1001 shipped.", first_status="requires_action", tool_call=call)
    assert reply(client, "thread_1", "where is A1001?", poll_seconds=0) == "Order A1001 shipped."
    sent = client.beta.threads.runs.submit_tool_outputs.call_args.kwargs["tool_outputs"]
    assert json.loads(sent[0]["output"])["status"] == "shipped"


def test_reply_raises_when_the_run_fails():
    with pytest.raises(RuntimeError):
        reply(fake_client(first_status="failed"), "thread_1", "hi", poll_seconds=0)
