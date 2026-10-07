from types import SimpleNamespace
from unittest.mock import MagicMock

from support_bot.streaming import WidgetEventHandler, stream_reply


def test_handler_collects_and_forwards_deltas():
    seen = []
    handler = WidgetEventHandler(seen.append)
    for part in ["Your ", "order ", "", "shipped."]:
        handler.on_text_delta(SimpleNamespace(value=part), None)
    assert handler.text == "Your order shipped."
    assert seen == ["Your ", "order ", "shipped."]


def test_stream_reply_posts_the_message_and_returns_streamed_text(client):
    def fake_stream(**kwargs):
        handler = kwargs["event_handler"]
        ctx = MagicMock()
        ctx.__enter__.return_value.until_done.side_effect = lambda: handler.on_text_delta(SimpleNamespace(value="Hi!"), None)
        return ctx

    client.beta.threads.runs.stream.side_effect = fake_stream
    assert stream_reply(client, "thread_1", "hello") == "Hi!"
    assert client.beta.threads.messages.create.call_args.kwargs["content"] == "hello"
