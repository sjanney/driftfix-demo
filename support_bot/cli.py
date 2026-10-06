"""Chat with the support bot in a terminal: python -m support_bot.cli"""

from .assistant import make_client, reply, start_conversation


def main():
    client = make_client()
    thread_id = start_conversation(client)
    print("Support bot ready. Ctrl-C to quit.")
    while True:
        text = input("> ").strip()
        if text:
            print(reply(client, thread_id, text))


if __name__ == "__main__":
    main()
