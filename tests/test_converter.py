import pytest
from src.converter import WebVTTConverter
import webvtt
from pathlib import Path
from tests.test_utils import check_identical_vtt_files

CAPTIONS_FILE = "tests/test_captions.vtt"
EMPTY_CAPTIONS_FILE = "tests/empty.vtt"
CONVERSIONS_FILE = "tests/test_conversions.json"
DEST_FILE = "tests/new_test_captions.vtt"
REFERENCE_DEST_FILE = "tests/reference_dest_captions.vtt"


@pytest.fixture()
def dest_file():
    yield DEST_FILE

    # checks if destination file is created and deletes it if so
    path = Path(DEST_FILE)
    if path.is_file():
        path.unlink()


def test_captions_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter("test.vtt", CONVERSIONS_FILE)
    assert str(exc_info.value) == "Captions file not found"


def test_captions_wrong_extension():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(CONVERSIONS_FILE, CONVERSIONS_FILE)
    assert str(exc_info.value) == "Captions file not found"


def test_conversions_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(CAPTIONS_FILE, "wrong_conversions.json")
    assert str(exc_info.value) == "Conversions file not found"


def test_conversions_wrong_extension():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = WebVTTConverter(CAPTIONS_FILE, "test.txt")
    assert str(exc_info.value) == "Conversions file not found"


def test_invalid_dest_extension():
    converter = WebVTTConverter(
        CAPTIONS_FILE, CONVERSIONS_FILE, dest_filename="wrong_filetype.txt"
    )
    assert str(converter.new_captions_path) == r"tests\test_captions-converted.vtt"


def test_valid_captions_and_conversions_files():
    converter = WebVTTConverter(
        captions_file=CAPTIONS_FILE, conversions_file="tests/test_conversions.json"
    )
    assert converter != None


def test_valid_captions_conversions_and_dest_files(dest_file):
    converter = WebVTTConverter(
        captions_file=CAPTIONS_FILE,
        conversions_file="tests/test_conversions.json",
        dest_filename=dest_file,
    )
    assert converter != None


def test_conversions(dest_file):
    converter = WebVTTConverter(
        captions_file=CAPTIONS_FILE,
        conversions_file="tests/test_conversions.json",
        dest_filename=dest_file,
    )
    converter.convert_captions()
    assert check_identical_vtt_files(dest_file, REFERENCE_DEST_FILE)


def test_empty_captions(dest_file):
    converter = WebVTTConverter(
        captions_file=EMPTY_CAPTIONS_FILE,
        conversions_file="tests/test_conversions.json",
        dest_filename=dest_file,
    )
    converter.convert_captions()
    assert len(webvtt.read(dest_file)) == 0
