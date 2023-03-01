import pytest
from src.converter import WebVTTConverter


CAPTIONS_FILE = "test_captions.vtt"
CAPTIONS_CONTENTS = ""
CONVERSIONS_FILE = "test_conversions.json"
CONVERSIONS_CONTENTS = ""


@pytest.fixture()
def captions_file(tmp_path):
    p = tmp_path / CAPTIONS_FILE
    p.touch()
    p.write_text(CAPTIONS_CONTENTS)
    yield p
    p.unlink()


@pytest.fixture()
def conversions_file(tmp_path):
    p = tmp_path / CONVERSIONS_FILE
    p.touch()
    p.write_text(CONVERSIONS_CONTENTS)
    yield p
    p.unlink()


def test_captions_not_found(conversions_file):
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter("test.vtt", conversions_file.name)
    assert str(exc_info.value) == "Captions file not found"


def test_captions_wrong_extension(conversions_file):
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(CONVERSIONS_FILE, conversions_file.name)
    assert str(exc_info.value) == "Captions file not found"


def test_conversions_not_found(captions_file):
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(captions_file.name, "wrong_conversions.json")
    assert str(exc_info.value) == "Conversions file not found"


def test_conversions_wrong_extension(captions_file):
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(captions_file.name, "test.txt")
    assert str(exc_info.value) == "Conversions file not found"
