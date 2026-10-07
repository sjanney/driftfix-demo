from .helpers import completion
from support_bot import drafts


def test_draft_only_states_given_facts(client):
    client.chat.completions.create.return_value = completion("Hi! Your order shipped.\n")
    assert drafts.draft_reply(client, "where is it", {"status": "shipped", "eta": "Oct 9"}) == "Hi! Your order shipped."
    system = client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
    assert "- eta: Oct 9\n- status: shipped" in system


def test_macro(client):
    client.chat.completions.create.return_value = completion("Hi {name}, sorry for the delay.")
    assert "{name}" in drafts.build_macro(client, "late delivery")
