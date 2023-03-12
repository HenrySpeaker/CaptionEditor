import pytest
from src.converter import WebVTTConverter, main
import webvtt
from pathlib import Path
from tests.test_utils import check_identical_vtt_files
import json
import copy
import argparse

CAPTIONS_FILE = "tests/test_captions.vtt"
EMPTY_CAPTIONS_FILE = "tests/empty.vtt"
CONVERSIONS_FILE = "tests/test_conversions.json"
INVALID_CONVERSIONS_FILE = "tests/invalid_conversions.json"
DEST_FILE = "tests/new_test_captions.vtt"
REFERENCE_DEST_FILE = "tests/reference_dest_captions.vtt"


@pytest.fixture()
def dest_file():
    yield DEST_FILE

    # checks if destination file is created and deletes it if so
    path = Path(DEST_FILE)
    if path.is_file():
        path.unlink()


@pytest.fixture()
def conversions_file_start():
    with open(INVALID_CONVERSIONS_FILE) as f:
        original_contents = json.load(f)
        yield copy.deepcopy(original_contents)

    with open(INVALID_CONVERSIONS_FILE, "w") as f:
        json.dump(original_contents, f)


@pytest.fixture()
def extra_conversions_contents(conversions_file_start):
    contents = conversions_file_start
    contents["extra_info"] = True
    with open(INVALID_CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return INVALID_CONVERSIONS_FILE


@pytest.fixture()
def large_pos_offset_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["offset"] = 1000000
    with open(INVALID_CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return INVALID_CONVERSIONS_FILE


@pytest.fixture()
def large_neg_offset_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["offset"] = -1000000
    with open(INVALID_CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return INVALID_CONVERSIONS_FILE


# @pytest.fixture()
# def negative_conversions_offset(conversions_file_start):
#     contents = copy.deepcopy(conversions_file_start)
#     contents["offset"] = -100000
#     with open(INVALID_CONVERSIONS_FILE, "w") as f:
#         json.dump(contents, f)

#     return INVALID_CONVERSIONS_FILE


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


def test_invalid_conversions_contents(extra_conversions_contents):
    with pytest.raises(ValueError) as exc_info:
        converter = WebVTTConverter(CAPTIONS_FILE, extra_conversions_contents)
    assert str(exc_info.value) == "Invalid conversions.json contents"


def test_large_pos_offset(large_pos_offset_conversions):
    converter = WebVTTConverter(CAPTIONS_FILE, large_pos_offset_conversions)
    converter.convert_captions()
    assert converter != None


def test_large_neg_offset(large_neg_offset_conversions):
    converter = WebVTTConverter(CAPTIONS_FILE, large_neg_offset_conversions)
    converter.convert_captions()
    assert converter != None


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


def test_valid_cli_arguments(dest_file):
    args = [CAPTIONS_FILE, "-c", CONVERSIONS_FILE, "-d", dest_file]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == dest_file


def test_missing_captions_cli_argument(dest_file):
    with pytest.raises(SystemExit) as exit_info:
        args = ["-c", CONVERSIONS_FILE, "-d", dest_file]
        args_out = main(args)
    assert exit_info.type == SystemExit
    assert exit_info.value.code == 2


def test_offset_cli_arg(dest_file):
    args = [CAPTIONS_FILE, "-c", CONVERSIONS_FILE, "-d", dest_file, "-o", "10"]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == dest_file
    assert args_out.o == "10"


def test_offset_zero_cli_arg(dest_file, capsys):
    args = [CAPTIONS_FILE, "-c", CONVERSIONS_FILE, "-d", dest_file, "-o", "0"]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == dest_file
    captured = capsys.readouterr()
    assert captured.out == "Offset must be nonzero.\n"


def test_cutoff(dest_file):
    converter = WebVTTConverter(CAPTIONS_FILE, CONVERSIONS_FILE, dest_file, cutoff=60)
    converter.convert_captions()
    assert len(webvtt.read(dest_file)) == 8
