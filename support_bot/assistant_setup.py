"""Creates and updates the remote support assistant (run once per deploy)."""

from . import config

INSTRUCTIONS = (
    "You are Acme's customer-support agent. Be brief and friendly. "
    "Look up orders and refunds with the tools before answering questions about them. "
    "Never promise a refund; say a teammate will review it."
)

FUNCTION_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the shipping status of an order.",
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string", "description": "e.g. A1001"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_refund_status",
            "description": "Look up the status of a refund request.",
            "parameters": {
                "type": "object",
                "properties": {"refund_id": {"type": "string", "description": "e.g. R2001"}},
                "required": ["refund_id"],
            },
        },
    },
]


def create_support_assistant(client, vector_store_id=None):
    """Create the assistant and return its id."""
    tools = list(FUNCTION_TOOLS)
    resources = None
    if vector_store_id:
        tools.append({"type": "file_search"})
        resources = {"file_search": {"vector_store_ids": [vector_store_id]}}
    assistant = client.beta.assistants.create(
        name="Acme Support",
        model=config.CHAT_MODEL,
        instructions=INSTRUCTIONS,
        tools=tools,
        tool_resources=resources,
        metadata={"team": "support"},
    )
    return assistant.id


def update_instructions(client, assistant_id, extra):
    """Append seasonal notes (holiday hours, outages) to the assistant's instructions."""
    current = client.beta.assistants.retrieve(assistant_id)
    return client.beta.assistants.update(
        assistant_id, instructions=f"{current.instructions}\n\n{extra}".strip()
    )


def list_support_assistants(client):
    """Ids of every assistant this team owns."""
    page = client.beta.assistants.list(limit=100)
    return [a.id for a in page.data if (a.metadata or {}).get("team") == "support"]
