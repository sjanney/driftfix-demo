from types import SimpleNamespace

import pytest

from support_bot.knowledge import answer_policy_question, close_conversation


def policy_client(client, status="completed"):
    client.beta.threads.create.return_value = SimpleNamespace(id="thread_9")
    client.beta.threads.runs.create_and_poll.return_value = SimpleNamespace(status=status)
    text = SimpleNamespace(
        value="Returns are accepted within 30 days.",
        annotations=[SimpleNamespace(file_citation=SimpleNamespace(file_id="file_returns")), SimpleNamespace(file_citation=None)],
    )
    client.beta.threads.messages.list.return_value = SimpleNamespace(data=[SimpleNamespace(content=[SimpleNamespace(text=text)])])
    return client


def test_answers_with_citations(client):
    answer, cites = answer_policy_question(policy_client(client), "Return window?", "vs_1")
    assert answer == "Returns are accepted within 30 days."
    assert cites == ["file_returns"]
    resources = client.beta.threads.create.call_args.kwargs["tool_resources"]
    assert resources == {"file_search": {"vector_store_ids": ["vs_1"]}}


def test_failed_lookup_raises(client):
    with pytest.raises(RuntimeError):
        answer_policy_question(policy_client(client, status="failed"), "Return window?", "vs_1")


def test_close_conversation(client):
    client.beta.threads.delete.return_value = SimpleNamespace(deleted=True)
    assert close_conversation(client, "thread_9") is True
