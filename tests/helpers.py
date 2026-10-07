from types import SimpleNamespace


def completion(content):
    """A chat-completions response with one choice."""
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
