from types import SimpleNamespace

from support_bot import assistant_setup


def test_create_registers_both_tools(client):
    client.beta.assistants.create.return_value = SimpleNamespace(id="asst_1")
    assert assistant_setup.create_support_assistant(client) == "asst_1"
    kwargs = client.beta.assistants.create.call_args.kwargs
    names = [t["function"]["name"] for t in kwargs["tools"]]
    assert names == ["get_order_status", "get_refund_status"]
    assert kwargs["tool_resources"] is None


def test_create_with_docs_adds_file_search(client):
    client.beta.assistants.create.return_value = SimpleNamespace(id="asst_2")
    assistant_setup.create_support_assistant(client, vector_store_id="vs_1")
    kwargs = client.beta.assistants.create.call_args.kwargs
    assert {"type": "file_search"} in kwargs["tools"]
    assert kwargs["tool_resources"] == {"file_search": {"vector_store_ids": ["vs_1"]}}


def test_update_appends_to_existing_instructions(client):
    client.beta.assistants.retrieve.return_value = SimpleNamespace(instructions="Be kind.")
    assistant_setup.update_instructions(client, "asst_1", "Closed on Dec 25.")
    assert client.beta.assistants.update.call_args.kwargs["instructions"] == "Be kind.\n\nClosed on Dec 25."


def test_list_keeps_only_support_assistants(client):
    client.beta.assistants.list.return_value = SimpleNamespace(data=[
        SimpleNamespace(id="a", metadata={"team": "support"}),
        SimpleNamespace(id="b", metadata={"team": "sales"}),
        SimpleNamespace(id="c", metadata=None),
    ])
    assert assistant_setup.list_support_assistants(client) == ["a"]
