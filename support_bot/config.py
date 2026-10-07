"""Model choices for every AI feature, in one place so ops can tune them."""

import os

# Conversational support agent (the Assistants-based bot) and its fallback.
CHAT_MODEL = os.environ.get("SUPPORT_CHAT_MODEL", "gpt-4-turbo")
CHEAP_MODEL = "gpt-3.5-turbo"

# Ticket triage runs on every inbound ticket, so it uses the smallest model.
TRIAGE_MODEL = "gpt-4.1-nano"

# Escalation decisions and refund-policy reasoning.
REASONING_MODEL = "o3-2025-04-16"

# First drafts of email replies that an agent reviews before sending.
DRAFT_MODEL = "gpt-5-mini-2025-08-07"

# Voice support line.
TRANSCRIBE_MODEL = "whisper-1"
VOICE_MODEL = "tts-1"

# Images for return labels and help-center articles.
IMAGE_MODEL = "gpt-image-1"
THUMBNAIL_MODEL = "gpt-image-1-mini"
