# Acme support platform (Driftfix demo)

A customer-support backend built on OpenAI: an Assistants-based chat bot with tools and file
search, ticket triage, escalation, summaries, reply drafts, a voice line and image generation.

It deliberately uses OpenAI APIs and models that are shut down or deprecated (and pins
`openai==1.40.0`) so [Driftfix](https://github.com/sjanney/driftfix) can show how it migrates real
code: it opens a pull request per upstream change, grounded in OpenAI's own deprecation notes,
and reports what the repo's tests say before and after.

| OpenAI change | Shutdown | Where this repo uses it |
| --- | --- | --- |
| Assistants API → Responses + Conversations | Aug 26, 2026 (already shut down) | `assistant.py`, `assistant_setup.py`, `streaming.py`, `knowledge.py` |
| Legacy GPT model snapshots | Oct 23, 2026 | `config.py` (`gpt-4-turbo`, `gpt-3.5-turbo`, `gpt-4.1-nano`, `gpt-image-1`), `summarizer.py`, `escalation.py` (`o1`), `drafts.py` |
| GPT Image model deprecations | Dec 1, 2026 | `config.py` (`gpt-image-1-mini`) |
| GPT-5 and o3 snapshots | Dec 11, 2026 | `config.py` (`o3-2025-04-16`, `gpt-5-mini-2025-08-07`) |
| Text-to-speech models | Jan 6, 2027 | `config.py` (`tts-1`) |
| Transcription models | Feb 26, 2027 | `config.py` (`whisper-1`), `voice.py` (`gpt-4o-transcribe-diarize`) |

Every module has tests with a mocked client (no API key or network needed):

```sh
pip install -r requirements.txt
pytest
```
