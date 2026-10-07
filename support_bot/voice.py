"""Voice support line: transcribes voicemails and reads replies aloud."""

from . import config


def transcribe_voicemail(client, audio_path):
    with open(audio_path, "rb") as audio:
        result = client.audio.transcriptions.create(model=config.TRANSCRIBE_MODEL, file=audio)
    return result.text


def transcribe_call(client, audio_path):
    """Full support calls, with who-said-what, for QA review."""
    with open(audio_path, "rb") as audio:
        result = client.audio.transcriptions.create(
            model="gpt-4o-transcribe-diarize", file=audio, response_format="diarized_json"
        )
    return [(seg.speaker, seg.text) for seg in result.segments]


def speak(client, text, out_path, voice="alloy"):
    """Render an answer to an MP3 for the phone system."""
    response = client.audio.speech.create(model=config.VOICE_MODEL, voice=voice, input=text)
    response.write_to_file(out_path)
    return out_path
