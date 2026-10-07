"""Customer-support bot built on the OpenAI Responses API."""

import inspect
import json
import os

from openai import OpenAI

from .orders import get_order_status
from .refunds import get_refund_status

# The Assistants API bundled the model, instructions, and tool definitions into
# a server-side assistant object. The Responses API needs those on each request,
# so they are configured here instead. Set SUPPORT_MODEL (and optionally
# SUPPORT_INSTRUCTIONS) to match the assistant you are migrating away from.
MODEL = os.environ.get("SUPPORT_MODEL", "gpt-6-astra")
INSTRUCTIONS = os.environ.get("SUPPORT_INSTRUCTIONS")

TOOLS = {"get_order_status": get_order_status, "get_refund_status": get_refund_status}


def make_client():
    return OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _build_tool_definitions():
    """Derive JSON-schema tool definitions from the callables in TOOLS.

    The Assistants API stored these schemas on the assistant object; the
    Responses API receives them on every request. Deriving the parameter names
    from the real function signatures avoids guessing what the assistant had.
    """
    definitions = []
    for name, fn in TOOLS.items():
        properties = {}
        required = []
        for param_name, param in inspect.signature(fn).parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.default is inspect.Parameter.empty:
                required.append(param_name)
            properties[param_name] = {"type": "string"}
        definitions.append(
            {
                "type": "function",
                "name": name,
                "description": (fn.__doc__ or "").strip() or f"Call the {name} function.",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                    "additionalProperties": False,
                },
            }
        )
    return definitions


TOOL_DEFINITIONS = _build_tool_definitions()


def start_conversation(client):
    """Create a conversation for a new support session and return its id."""
    return client.conversations.create(metadata={"source": "support-bot"}).id


def _tool_outputs(response):
    """Execute every function call in a response and format the results."""
    outputs = []
    for item in response.output:
        if item.type != "function_call":
            continue
        fn = TOOLS[item.name]
        args = json.loads(item.arguments or "{}")
        outputs.append(
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(fn(**args)),
            }
        )
    return outputs


def _create_response(client, conversation_id, input_items):
    kwargs = {
        "model": MODEL,
        "input": input_items,
        "conversation": conversation_id,
        "tools": TOOL_DEFINITIONS,
    }
    if INSTRUCTIONS:
        kwargs["instructions"] = INSTRUCTIONS
    return client.responses.create(**kwargs)


def reply(client, conversation_id, text, poll_seconds=0.5):
    """Send the customer's message and return the assistant's answer."""
    response = _create_response(client, conversation_id, [{"role": "user", "content": text}])

    while True:
        if response.status == "requires_action":
            response = _create_response(client, conversation_id, _tool_outputs(response))
            continue
        if response.status != "completed":
            raise RuntimeError(f"assistant response ended with status {response.status}")
        break

    return response.output_text
