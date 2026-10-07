"""Answers help-center questions from uploaded policy documents (file search)."""

from .assistant import ASSISTANT_ID


def answer_policy_question(client, question, vector_store_id):
    """One-off question against the policy docs; returns (answer, citations)."""
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": question}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        additional_instructions="Answer only from the attached policy documents. Cite them.",
    )
    if run.status != "completed":
        raise RuntimeError(f"policy lookup ended with status {run.status}")
    message = client.beta.threads.messages.list(thread_id=thread.id, order="desc", limit=1).data[0]
    text = message.content[0].text
    citations = [a.file_citation.file_id for a in text.annotations if getattr(a, "file_citation", None)]
    return text.value, citations


def close_conversation(client, thread_id):
    """Delete a finished conversation (GDPR retention: 30 days)."""
    return client.beta.threads.delete(thread_id).deleted
