"""Customer-support bot built on the OpenAI Assistants API."""

import json
import os
import time

from openai import OpenAI

from .orders import get_order_status

ASSISTANT_ID = os.environ.get("SUPPORT_ASSISTANT_ID", "asst_support")

TOOLS = {"get_order_status": get_order_status}


def make_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def start_conversation(client):
    """Create a thread for a new support conversation and return its id."""
    return client.beta.threads.create(metadata={"source": "support-bot"}).id


def _run_tools(client, thread_id, run):
    outputs = []
    for call in run.required_action.submit_tool_outputs.tool_calls:
        fn = TOOLS[call.function.name]
        args = json.loads(call.function.arguments or "{}")
        outputs.append({"tool_call_id": call.id, "output": json.dumps(fn(**args))})
    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id, run_id=run.id, tool_outputs=outputs
    )


def reply(client, thread_id, text, poll_seconds=0.5):
    """Send the customer's message and return the assistant's answer."""
    client.beta.threads.messages.create(thread_id=thread_id, role="user", content=text)
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=ASSISTANT_ID)

    while run.status in ("queued", "in_progress", "requires_action"):
        if run.status == "requires_action":
            run = _run_tools(client, thread_id, run)
            continue
        time.sleep(poll_seconds)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    if run.status != "completed":
        raise RuntimeError(f"assistant run ended with status {run.status}")

    messages = client.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=1)
    return messages.data[0].content[0].text.value
