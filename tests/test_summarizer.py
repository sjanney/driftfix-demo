from .helpers import completion
from support_bot import summarizer

TICKET = [("customer", "My blender arrived broken."), ("agent", "Sorry! Photo please?"), ("customer", "Attached.")]


def test_summary_includes_the_whole_thread(client):
    client.chat.completions.create.return_value = completion("  - Blender arrived broken\n")
    assert summarizer.summarize_ticket(client, TICKET) == "- Blender arrived broken"
    sent = client.chat.completions.create.call_args.kwargs["messages"][1]["content"]
    assert "customer: Attached." in sent


def test_headline_strips_quotes(client):
    client.chat.completions.create.return_value = completion('"Broken blender on arrival"')
    assert summarizer.headline(client, TICKET) == "Broken blender on arrival"
