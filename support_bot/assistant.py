"""Customer-support bot built on the OpenAI Responses API."""

import json
import os

from openai import OpenAI

from .orders import get_order_status

# The Assistant's instruction + tool bundle previously lived server-side as an
# Assistant object. Create a matching Prompt in the dashboard and store its ID
# here. (Reusable prompt objects are deprecated Nov 30, 2026 — eventually inline
# the prompt content in this file instead.)
PROMPT_ID = os.environ.get("SUPPORT_PROMPT_ID", "pmpt_support")

# Tool schemas previously defined on the Assistant object server-side.
# Configure via SUPPORT_TOOLS JSON env var, e.g.:
#   [{"type":"function","name":"get_order_status",
#     "description":"Get the status of an order.",
#     "parameters":{"type":"object","properties":{
#       "order_id":{"type":"string","description":"Order ID"}}
#      "required":["order_id"],"additionalProperties":false}}]
TOOL_SCHEMAS = json.loads(os.environ.get("SUPPORT_TOOLS", "[]"))
TOOL_FUNCTIONS = {"get_order_status": get_order_status}


def make_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def start_conversation(client):
    """Create a conversation for a new support session and return its id."""
    return client.conversations.create(metadata={"source": "support-bot"}).id


def _execute_tool(call):
    fn = TOOL_FUNCTIONS[call.name]
    args = json.loads(call.arguments or "{}")
    return json.dumps(fn(**args))


def reply(client, conversation_id, text, poll_seconds=0.5):
    """Send the customer's message and return the assistant's answer."""
    input_items = [{"role": "user", "content": text}]

    while True:
        try:
            response = client.responses.create(
                model=os.environ.get("SUPPORT_MODEL", "gpt-6-astra"),
                prompt={"id": PROMPT_ID},
                tools=TOOL_SCHEMAS,
                input=input_items,
                conversation=conversation_id,
            )
        except Exception as e:
            raise RuntimeError(f"assistant response failed: {e}") from e

        if response.error:
            raise RuntimeError(f"assistant response failed: {response.error}")

        tool_calls = [item for item in response.output if item.type == "function_call"]
        if not tool_calls:
            return response.output_text

        input_items += response.output
        for call in tool_calls:
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": _execute_tool(call),
                }
            )
