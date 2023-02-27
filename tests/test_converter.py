import pytest
from src.converter import Converter


def test_captions_not_found():
    with pytest.raises(FileNotFoundError):
        converter = Converter("test.vtt", "test.txt")
