from unittest.mock import MagicMock

import pytest


@pytest.fixture
def client():
    return MagicMock()
