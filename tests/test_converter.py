import pytest
from src.captionconverter import CaptionConverter
from src.captionconverter.converter import main
import webvtt
from pathlib import Path
from tests.test_utils import check_identical_contents
import json
import copy

# Files and filenames to test naming
CAPTIONS_FILE_NAME = "test_vtt"
CAPTIONS_FILE = "tests/test_data/initial_captions/" + CAPTIONS_FILE_NAME + ".vtt"

# Initial files to test conversions
INITIAL_CAPTIONS_ROOT = "tests/test_data/initial_captions/"
DFXP_CAPTIONS = INITIAL_CAPTIONS_ROOT + "test_dfxp.dfxp"
SRT_CAPTIONS = INITIAL_CAPTIONS_ROOT + "test_srt.srt"
TTML_CAPTIONS = INITIAL_CAPTIONS_ROOT + "test_ttml.ttml"
VTT_CAPTIONS = INITIAL_CAPTIONS_ROOT + "test_vtt.vtt"
EMPTY_CAPTIONS_FILE = INITIAL_CAPTIONS_ROOT + "empty.vtt"

# Conversions files
CONVERSIONS_ROOT = "tests/test_data/conversions/"
CONVERSIONS_FILE = CONVERSIONS_ROOT + "conversions.json"

# Reference files after conversion
CONVERTED_CAPTIONS_ROOT = "tests/test_data/converted_captions/"
CONVERTED_DFXP = CONVERTED_CAPTIONS_ROOT + "converted.dfxp"
CONVERTED_SRT = CONVERTED_CAPTIONS_ROOT + "converted.srt"
CONVERTED_TTML = CONVERTED_CAPTIONS_ROOT + "converted.ttml"
CONVERTED_VTT = CONVERTED_CAPTIONS_ROOT + "converted.vtt"

# Temporary files to be cleaned up after
TEMP_DEST_DIR = "tests/test_data/"
TEMP_DEST_FILE = "temp_test_captions.vtt"


@pytest.fixture()
def dest_file():
    yield {"directory": TEMP_DEST_DIR, "name": TEMP_DEST_FILE}

    # checks if destination file is created and deletes it if so
    path = Path(TEMP_DEST_DIR) / TEMP_DEST_FILE
    if path.is_file():
        path.unlink()


@pytest.fixture(
    params=[
        (DFXP_CAPTIONS, "dfxp.dfxp", CONVERTED_CAPTIONS_ROOT, CONVERTED_DFXP, ".dfxp"),
        (SRT_CAPTIONS, "srt.srt", CONVERTED_CAPTIONS_ROOT, CONVERTED_SRT, ".srt"),
        (TTML_CAPTIONS, "ttml.ttml", CONVERTED_CAPTIONS_ROOT, CONVERTED_TTML, ".ttml"),
        (VTT_CAPTIONS, "vtt.vtt", CONVERTED_CAPTIONS_ROOT, CONVERTED_VTT, ".vtt"),
    ]
)
def test_files(request):
    yield request

    captions, dest, root, reference, type = request.param
    # checks if destination file is created and deletes it if so
    path = Path(root) / dest
    if path.is_file():
        path.unlink()


@pytest.fixture()
def conversions_file_start():
    with open(CONVERSIONS_FILE) as f:
        original_contents = json.load(f)
        yield copy.deepcopy(original_contents)

    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(original_contents, f)


@pytest.fixture()
def extra_conversions_contents(conversions_file_start):
    contents = conversions_file_start
    contents["extra_info"] = True
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


@pytest.fixture()
def large_pos_offset_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["offset"] = 1000000
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


@pytest.fixture()
def large_neg_offset_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["offset"] = -1000000
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


@pytest.fixture()
def string_offset_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["offset"] = "hello world"
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


@pytest.fixture()
def dict_conversions(conversions_file_start):
    contents = conversions_file_start
    contents["conversions"] = {}
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


@pytest.fixture()
def all_conversion_types(conversions_file_start):
    contents = conversions_file_start
    contents["conversions"].append({"key": "hello world"})
    contents["conversions"].append({"replacement": "hello world"})
    contents["conversions"].append({"key": "hello world", "replacement": "hello world"})
    with open(CONVERSIONS_FILE, "w") as f:
        json.dump(contents, f)

    return CONVERSIONS_FILE


def test_captions_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = CaptionConverter("test.vtt", CONVERSIONS_FILE)
    assert str(exc_info.value) == "Captions file not found"


def test_captions_wrong_extension():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = CaptionConverter(CONVERSIONS_FILE, CONVERSIONS_FILE)
    assert str(exc_info.value) == "Captions file not found"


def test_conversions_not_found():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = CaptionConverter(VTT_CAPTIONS, "wrong_conversions.json")
    assert str(exc_info.value) == "Conversions file not found"


def test_conversions_wrong_extension():
    with pytest.raises(FileNotFoundError) as exc_info:
        converter = CaptionConverter(VTT_CAPTIONS, "test.txt")
    assert str(exc_info.value) == "Conversions file not found"


def test_invalid_conversions_contents(extra_conversions_contents):
    with pytest.raises(ValueError) as exc_info:
        converter = CaptionConverter(VTT_CAPTIONS, extra_conversions_contents)
    assert str(exc_info.value) == "Invalid conversions.json contents"


def test_large_pos_offset(large_pos_offset_conversions, dest_file):
    converter = CaptionConverter(
        CAPTIONS_FILE,
        large_pos_offset_conversions,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
    )
    converter.convert_captions()
    assert converter != None


def test_large_neg_offset(large_neg_offset_conversions, dest_file):
    converter = CaptionConverter(
        CAPTIONS_FILE,
        large_neg_offset_conversions,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
    )
    converter.convert_captions()
    assert converter != None


def test_dest_filename_same_as_captions():
    converter = CaptionConverter(
        CAPTIONS_FILE,
        CONVERSIONS_FILE,
        dest_filename=CAPTIONS_FILE_NAME,
        dest_directory=INITIAL_CAPTIONS_ROOT,
    )
    assert converter._dest_filename == CAPTIONS_FILE_NAME + "-converted"


def test_dest_filename_same_as_captions_diff_directory():
    converter = CaptionConverter(
        CAPTIONS_FILE,
        CONVERSIONS_FILE,
        dest_filename=CAPTIONS_FILE_NAME,
        dest_directory=TEMP_DEST_DIR,
    )
    assert converter._dest_filename == CAPTIONS_FILE_NAME


def test_valid_captions_and_conversions_files():
    converter = CaptionConverter(
        captions_file=CAPTIONS_FILE,
        conversions_file=CONVERSIONS_FILE,
    )
    assert converter != None


def test_valid_captions_conversions_and_dest_files(dest_file):
    converter = CaptionConverter(
        captions_file=CAPTIONS_FILE,
        conversions_file=CONVERSIONS_FILE,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
    )
    assert converter != None


def test_string_offset(string_offset_conversions):
    with pytest.raises(ValueError) as exc_info:
        converter = CaptionConverter(CAPTIONS_FILE, string_offset_conversions)
    assert str(exc_info.value) == "Offset must be integer"


def test_dict_conversions(dict_conversions):
    with pytest.raises(ValueError) as exc_info:
        converter = CaptionConverter(CAPTIONS_FILE, dict_conversions)
    assert str(exc_info.value) == "Conversions must be list"


def test_empty_captions(dest_file):
    converter = CaptionConverter(
        captions_file=EMPTY_CAPTIONS_FILE,
        conversions_file=CONVERSIONS_FILE,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
    )
    converter.convert_captions()
    assert not Path(dest_file["name"]).is_file()


def test_valid_cli_arguments():
    args = [CAPTIONS_FILE, "-c", CONVERSIONS_FILE, "-d", TEMP_DEST_FILE, "-co", "0"]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == TEMP_DEST_FILE


def test_missing_captions_cli_argument():
    with pytest.raises(SystemExit) as exit_info:
        args = ["-c", CONVERSIONS_FILE, "-d", TEMP_DEST_FILE]
        args_out = main(args)
    assert exit_info.type == SystemExit
    assert exit_info.value.code == 2


def test_offset_cli_arg(dest_file):
    args = [
        CAPTIONS_FILE,
        "-c",
        CONVERSIONS_FILE,
        "-d",
        dest_file["name"],
        "-dd",
        dest_file["directory"],
        "-o",
        "10",
    ]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == dest_file["name"]
    assert args_out.dd == dest_file["directory"]
    assert args_out.o == "10"


def test_offset_zero_cli_arg(capsys):
    args = [CAPTIONS_FILE, "-c", CONVERSIONS_FILE, "-d", TEMP_DEST_FILE, "-o", "0"]
    args_out = main(args)
    assert args_out.caption_filename == CAPTIONS_FILE
    assert args_out.c == CONVERSIONS_FILE
    assert args_out.d == TEMP_DEST_FILE
    captured = capsys.readouterr()
    assert captured.out == "Offset must be nonzero.\n"


def test_cutoff(dest_file):
    converter = CaptionConverter(
        CAPTIONS_FILE,
        CONVERSIONS_FILE,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
        cutoff=100,
    )
    converter.convert_captions()
    assert len(webvtt.read(Path(dest_file["directory"]) / dest_file["name"])) == 18


def test_multiple_extensions(test_files):
    captions, dest, root, reference, type = test_files.param
    converter = CaptionConverter(
        captions_file=captions,
        conversions_file=CONVERSIONS_FILE,
        dest_filename=dest,
        dest_directory=root,
        dest_file_extensions=[type],
    )
    converter.convert_captions()
    assert check_identical_contents(Path(root) / dest, reference)


def test_all_conversion_types(all_conversion_types, dest_file):
    converter = CaptionConverter(
        CAPTIONS_FILE,
        all_conversion_types,
        dest_filename=dest_file["name"],
        dest_directory=dest_file["directory"],
    )
    assert converter != None


def test_update_invalid_directory():
    converter = CaptionConverter(CAPTIONS_FILE, CONVERSIONS_FILE)
    with pytest.raises(FileNotFoundError) as exc_info:
        converter.update_dest_directory("NOT A DIRECTORY")
    assert str(exc_info.value) == "The destination directory does not exist."


def test_dest_dir_as_path():
    converter = CaptionConverter(
        CAPTIONS_FILE, CONVERSIONS_FILE, dest_directory=Path("tests/test_data")
    )
    assert converter != None
