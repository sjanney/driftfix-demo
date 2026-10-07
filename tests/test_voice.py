from types import SimpleNamespace

from support_bot import voice


def test_transcribe_voicemail(client, tmp_path):
    audio = tmp_path / "vm.mp3"
    audio.write_bytes(b"ID3")
    client.audio.transcriptions.create.return_value = SimpleNamespace(text="Call me back please")
    assert voice.transcribe_voicemail(client, audio) == "Call me back please"


def test_transcribe_call_keeps_speakers(client, tmp_path):
    audio = tmp_path / "call.mp3"
    audio.write_bytes(b"ID3")
    client.audio.transcriptions.create.return_value = SimpleNamespace(segments=[
        SimpleNamespace(speaker="A", text="Hi"), SimpleNamespace(speaker="B", text="Hello"),
    ])
    assert voice.transcribe_call(client, audio) == [("A", "Hi"), ("B", "Hello")]


def test_speak_writes_the_audio(client, tmp_path):
    out = tmp_path / "answer.mp3"
    assert voice.speak(client, "Your order shipped", out) == out
    client.audio.speech.create.return_value.write_to_file.assert_called_once_with(out)
