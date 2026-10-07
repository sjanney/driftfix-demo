import base64
from types import SimpleNamespace

from support_bot import images


def png_result(client):
    client.images.generate.return_value = SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(b"PNG").decode())])
    return client


def test_return_label_art_decodes_the_image(client):
    assert images.return_label_art(png_result(client), "blender") == b"PNG"
    assert "blender" in client.images.generate.call_args.kwargs["prompt"]


def test_thumbnail_is_low_quality(client):
    assert images.article_thumbnail(png_result(client), "Returns") == b"PNG"
    assert client.images.generate.call_args.kwargs["quality"] == "low"
