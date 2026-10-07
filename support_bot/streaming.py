"""Streams the assistant's reply token by token for the web chat widget."""

from openai import AssistantEventHandler

from .assistant import ASSISTANT_ID


class WidgetEventHandler(AssistantEventHandler):
    """Collects streamed text and forwards each delta to the widget."""

    def __init__(self, on_delta=None):
        super().__init__()
        self.on_delta = on_delta or (lambda text: None)
        self.parts = []

    def on_text_delta(self, delta, snapshot):
        if delta.value:
            self.parts.append(delta.value)
            self.on_delta(delta.value)

    @property
    def text(self):
        return "".join(self.parts)


def stream_reply(client, thread_id, text, on_delta=None):
    """Send the customer's message and stream the answer; returns the full text."""
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=text)
    handler = WidgetEventHandler(on_delta)
    with client.beta.threads.runs.stream(
        thread_id=thread_id, assistant_id=ASSISTANT_ID, event_handler=handler
    ) as stream:
        stream.until_done()
    return handler.text
