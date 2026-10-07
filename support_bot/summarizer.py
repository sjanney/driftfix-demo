"""Summarizes long ticket threads for the agent who picks them up next."""

SYSTEM = "Summarize this support ticket for a support agent in at most 5 bullet points."


def summarize_ticket(client, messages):
    """messages: list of (author, text). Returns the summary text."""
    transcript = "\n".join(f"{author}: {text}" for author, text in messages)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": transcript}],
        temperature=0.2,
    )
    return completion.choices[0].message.content.strip()


def headline(client, messages):
    """A one-line subject for the ticket list."""
    transcript = "\n".join(text for _, text in messages[:3])
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Write a 6-word subject line for:\n{transcript}"}],
        max_tokens=20,
    )
    return completion.choices[0].message.content.strip().strip('"')
