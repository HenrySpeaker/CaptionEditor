import pytest
from src.converter import WebVTTConverter


def test_captions_not_found():
    with pytest.raises(FileNotFoundError):
        converter = WebVTTConverter("test.vtt", "test.txt")
