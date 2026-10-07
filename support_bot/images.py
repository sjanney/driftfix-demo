"""Generates illustrations for return labels and help-center articles."""

import base64

from . import config


def return_label_art(client, product_name):
    result = client.images.generate(
        model=config.IMAGE_MODEL,
        prompt=f"A friendly flat illustration of a {product_name} in a shipping box, white background",
        size="1024x1024",
    )
    return base64.b64decode(result.data[0].b64_json)


def article_thumbnail(client, title):
    result = client.images.generate(
        model=config.THUMBNAIL_MODEL,
        prompt=f"Minimal icon for a help-center article titled '{title}'",
        size="1024x1024",
        quality="low",
    )
    return base64.b64decode(result.data[0].b64_json)
