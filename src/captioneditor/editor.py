import webvtt
import argparse
from pathlib import Path
import json
import re
import sys
from flashtext2 import KeywordProcessor
from pycaption import (
    WebVTTReader,
    SRTReader,
    DFXPReader,
    WebVTTWriter,
    SRTWriter,
    DFXPWriter,
    CaptionReadNoCaptions,
)

SUPPORTED_FILE_TYPES = {".vtt", ".srt", ".ttml", ".dfxp"}


class Editor:
    READERS = {
        ".vtt": WebVTTReader(),
        ".srt": SRTReader(),
        ".ttml": DFXPReader(),
        ".dfxp": DFXPReader(),
    }

    WRITERS = {
        ".vtt": WebVTTWriter(),
        ".srt": SRTWriter(),
        ".ttml": DFXPWriter(),
        ".dfxp": DFXPWriter(),
    }

    def __init__(
        self,
        captions_file: str | Path,
        conversions_file: Path | str = "conversions.json",
        dest_filename: str = "",
        dest_file_extensions: list[str] = [".vtt"],
        dest_directory: Path | str = "",
        offset: int = 0,
        cutoff: float | int = -1,
    ) -> None:
        # Validate and store the captions file. Check that it exists and has a correct extension.
        self._captions_file_path: Path = Path()
        self.update_captions_path(captions_file)

        # Store the destination directory, verifying that it exists
        self._dest_directory: Path = Path()
        self.update_dest_directory(dest_directory)

        # Store the destination filename template, creating a new one if necessary
        self._dest_filename = ""
        self.update_dest_filename(dest_filename)

        # Store the destination filetypes, verifying that they are all valid types
        self._dest_filetypes = []

        if dest_file_extensions:
            for extension in dest_file_extensions:
                if extension in self.READERS:
                    self._dest_filetypes.append(extension)
        else:
            self._dest_filetypes = [".vtt"]

        self.conversions_file_path: Path = Path()

        # Initialize everything that might be needed for caption conversions
        self.timing_offset = offset
        self.cutoff: int = -1
        self._conversions: list = []

        self._case_sensitive_processor = KeywordProcessor(case_sensitive=True)
        self._case_insensitive_processor = KeywordProcessor()
        self._previous_caption_keys_processor = KeywordProcessor(case_sensitive=True)
        self._previous_caption_keys: list = []
        self._previous_captions_processors: dict = {}
        self._direct_conversions: dict = {}

        # If no offset value was provided or if it was zero, check for and process a conversions file
        # If an offset is provided, it is assumed that no conversions are desired and the captions only need to be offset
        if offset == 0:
            self.update_conversions(conversions_file)

        if cutoff >= 0:
            self.update_cutoff(cutoff)

    def _store_conversions(self) -> None:
        """
        Store conversions file data.
        """

        # Gather conversions data from file
        with open(self.conversions_file_path) as conversions_json:
            conversions_data = json.load(conversions_json)

        # Verify that the structure of the file matches what's expected
        if len(conversions_data) > 3 or any(
            key not in ("offset", "cutoff", "conversions")
            for key in conversions_data.keys()
        ):
            raise ValueError("Invalid conversions.json contents")

        # Set the offset and the list of conversions

        if "offset" in conversions_data:
            if not isinstance(conversions_data["offset"], int):
                raise ValueError("Offset must be integer")
            else:
                self.timing_offset = conversions_data["offset"]
        else:
            self.timing_offset = 0

        if "cutoff" in conversions_data:
            if not isinstance(conversions_data["cutoff"], int):
                raise ValueError("Cutoff must be integer")
            else:
                self.cutoff = conversions_data["cutoff"]
        else:
            self.cutoff = -1

        if not isinstance(conversions_data["conversions"], list):
            raise ValueError("Conversions must be list")

        self._conversions = conversions_data["conversions"]

    def _process_caption_contents(self, caption_text: str = "") -> str:
        """
        Replaces any kewords in current caption and records any keys seen that would be relevant for the next caption.
        """

        # First check for any captions that should be converted directly
        if caption_text in self._direct_conversions:
            return self._direct_conversions[caption_text]

        # Process caption through both the case-senstive and case-insentive processors
        caption_text = self._case_insensitive_processor.replace_keywords(caption_text)
        caption_text = self._case_sensitive_processor.replace_keywords(caption_text)

        # If any previous caption keys were matched in the previous caption, iterate through them and process the current caption as appropriate
        for key in self._previous_caption_keys:
            caption_text = self._previous_captions_processors[key].replace_keywords(
                caption_text
            )

        # Check the current caption for any matches in the previous caption keys so that they're ready when the next caption is processed
        self._previous_caption_keys = (
            self._previous_caption_keys_processor.extract_keywords(caption_text)
        )
        return caption_text

    def _create_new_dest_filename(self) -> None:
        """
        If there is no name or no appropriate name for the destination file, a name will be created based on the original file, with '-converted' appended to the filename's stem.
        """

        # Add '-converted' to the end of the stem of the current caption file path so the converted captions are distinguished from the original
        original_name = self._captions_file_path.stem
        self._dest_filename = original_name + "-converted"

    def _build_keyword_processors(self) -> None:
        """
        Uses the conversions data and creates keyword processors for case-sensitive, case-insensitive, and any other keys that are replaced based on previous captions.
        """

        # These processors look for simple matches and replace them
        self._case_sensitive_processor = KeywordProcessor(case_sensitive=True)
        self._case_insensitive_processor = KeywordProcessor()

        # This processor looks for matches in the current caption that will be used for conversions in the following caption
        self._previous_caption_keys_processor = KeywordProcessor(case_sensitive=True)

        # This stores any keys found from the previous captions processor so that they can be referenced when processing the following caption
        self._previous_caption_keys = []

        # This stores the processors that are meant to process the following caption and are keyed to the matches that could be found in the previous caption
        self._previous_captions_processors = {}

        # This stores any conversions that are meant to process an entire caption that matches exactly and replace it with new contents
        self._direct_conversions = {}

        for conversion in self._conversions:
            if "key" not in conversion:
                continue
            if "replacement" not in conversion:
                continue
            key = conversion["key"]
            replacement = conversion["replacement"]

            # First check if the current conversion is dependent on a match occuring in the preceding caption
            if "previous" in conversion and conversion["previous"]:
                self._previous_caption_keys_processor.add_keyword(
                    conversion["previous"]
                )
                self._previous_captions_processors[
                    conversion["previous"]
                ] = KeywordProcessor(case_sensitive=True)
                self._previous_captions_processors[conversion["previous"]].add_keyword(
                    key, replacement
                )

            # These are the captions meant to be converted directly, without any partial replacement
            elif "directConversion" in conversion and conversion["directConversion"]:
                self._direct_conversions[conversion["key"]] = conversion["replacement"]
            else:
                if "caseSensitive" in conversion and conversion["caseSensitive"]:
                    self._case_sensitive_processor.add_keyword(key, replacement)
                else:
                    self._case_insensitive_processor.add_keyword(key, replacement)

    def update_cutoff(self, new_cutoff: int | float) -> None:
        """
        Updates the time cutoff (in seconds) for captions to be written. Any captions, after the offset has been applied, that would occur after the cutoff will not be included.
        """
        self.cutoff = new_cutoff

    def update_captions_path(self, captions_file: str | Path) -> None:
        """
        Check if provided file string or path exists and is of a valid type, update the file path property. If it isn't, raise an error.
        """

        self._captions_file_path = Path(captions_file)
        if (
            not self._captions_file_path.is_file()
            or self._captions_file_path.suffix not in self.READERS
        ):
            self._captions_file_path = Path()
            raise FileNotFoundError("Captions file not found")

    def update_conversions(self, conversions: str | Path) -> None:
        """
        Accepts a string of the relative or absolute path to conversions file and checks if conversions file exists. If it does exist, its contents are processed and stored in the converter.
        """

        self.conversions_file_path = Path(conversions)
        if (
            not self.conversions_file_path.is_file()
            or self.conversions_file_path.suffix != ".json"
        ):
            self.conversions_file_path = Path()
            raise FileNotFoundError("Conversions file not found")
        self._store_conversions()
        self._build_keyword_processors()

    def update_dest_filename(self, new_name: str = "") -> None:
        """
        Check for supplied filename for output file and create one if necessary. If no filename,
        or the same filename as the original captions file is supplied and the destination directory is the same, a new filename will be created.
        """

        if new_name:
            if (
                new_name == self._captions_file_path.stem
                and self._captions_file_path.parent == self._dest_directory
            ):
                self._create_new_dest_filename()
            else:
                self._dest_filename = new_name
        else:
            self._create_new_dest_filename()

    def update_dest_directory(self, new_directory: Path | str = ""):
        """
        Accepts a string of the path to the destination directory, verifies that the new destination directory exists, and sets the new destination directory.
        """
        test_path = Path(new_directory)
        if not new_directory:
            self._dest_directory = self._captions_file_path.parent
        if test_path.is_dir():
            self._dest_directory = test_path
        else:
            raise FileNotFoundError("The destination directory does not exist.")

    def edit_captions(self) -> None:
        """
        Reads captions from captions file, converts them based on offset, cutoff, and conversions file, and writes them to the destination file(s) in the destination directory.
        """

        timestamp_pattern = re.compile(r"((\d{2,}):)?(\d\d):(\d\d).(\d\d\d)")

        def offset_time(time):
            time_info = timestamp_pattern.search(time).groups()
            hours = int(time_info[1]) if time_info[1] else 0
            minutes = int(time_info[2])
            seconds = int(time_info[3])
            milliseconds = int(time_info[4]) + self.timing_offset

            while milliseconds >= 1000:
                seconds += 1
                milliseconds -= 1000

            while milliseconds < 0:
                milliseconds += 1000
                seconds -= 1

            while seconds >= 60:
                minutes += 1
                seconds -= 60

            while seconds < 0:
                seconds += 60
                minutes -= 1

            while minutes >= 60:
                hours += 1
                minutes -= 60

            while minutes < 0:
                minutes += 60
                hours -= 1

            # Since negative timestamps aren't valid in WebVTT, None is returned to signal that the current caption should not be included in the new file
            if min(hours, minutes, seconds, milliseconds) < 0:
                return (None, 0)

            new_time = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}.{str(milliseconds).zfill(3)}"
            return (
                new_time,
                hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
            )

        # Check if captions file is not already VTT and convert it to a temporary VTT file if necessary
        captions_type = self._captions_file_path.suffix
        vtt_captions_path = None
        vtt_contents = ""
        if captions_type != ".vtt":
            reader = self.READERS[captions_type]

            with open(self._captions_file_path, "r", encoding="utf8") as file:
                raw_contents = file.read()

            contents_caption_set = reader.read(raw_contents)
            vtt_contents = WebVTTWriter().write(contents_caption_set)

            temp_vtt_path = self._captions_file_path.with_stem(
                self._captions_file_path.stem + "-temp"
            )

            with open(temp_vtt_path, "w", encoding="utf8") as file:
                file.write(vtt_contents)

            vtt_captions_path = temp_vtt_path
        else:
            vtt_captions_path = self._captions_file_path

        # Modify the captions from the VTT file
        new_file_contents = "WEBVTT - Converted from " + str(vtt_captions_path)
        caption_count = 0

        for caption in webvtt.read(vtt_captions_path):
            start_time = caption.start
            new_start, seconds_after_start = offset_time(start_time)

            end_time = caption.end
            new_end, _ = offset_time(end_time)

            if not new_start:
                continue

            if self.cutoff >= 0 and seconds_after_start > self.cutoff:
                continue

            new_caption = "\n" * 2 + str(caption_count) + "\n"
            new_caption += new_start + " --> " + new_end + "\n"
            new_caption += self._process_caption_contents(caption.text)

            new_file_contents += new_caption
            caption_count += 1

        try:
            new_caption_set = WebVTTReader().read(new_file_contents)
        except CaptionReadNoCaptions:
            print("Cannot convert an empty captions file")
            return

        # Convert captions to all specified file types
        for extension in self._dest_filetypes:
            writer = self.WRITERS[extension]
            dest_file_path = Path(
                self._dest_directory / self._dest_filename
            ).with_suffix(extension)
            curr_contents = writer.write(new_caption_set)

            with open(dest_file_path, "w", encoding="utf8") as new_file:
                new_file.write(curr_contents)

        # Clean up any temporary files if needed. Look for a starting VTT file that is temporary and a captions-converted VTT file if that's not needed in the file output.
        if vtt_captions_path != self._captions_file_path:
            if vtt_captions_path.is_file():
                vtt_captions_path.unlink()


def main(args=None) -> argparse.Namespace:
    if not args:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("caption_filename", type=str, help="the file to be converted")
    parser.add_argument(
        "-c",
        "-conversions",
        type=str,
        default="conversions.json",
        required=False,
        help="the text file containing the conversion rules",
    )
    parser.add_argument(
        "-d",
        "-destination",
        help="optional destination filename, default is '<previous filename>-converted.vtt'",
    )
    parser.add_argument(
        "-o",
        "-offset",
        help="Optional offset value (in ms) for the converter. If this is supplied, no conversions will be used from a .json file and only the offset will be applied.",
        required=False,
    )
    parser.add_argument(
        "-dt",
        "-dest_types",
        help="Optional list of filetypes that captions will be converted to. Default is WebVTT only.",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "-dd",
        "-dest_dir",
        help="A directory that already exists that all converted files should be written in.",
        default="",
    )
    parser.add_argument(
        "-co",
        "-cutoff",
        help="An integer (in seconds) that specifies the timestamp after which no more captions should occur.",
        default=0,
    )
    args = parser.parse_args(args)
    cutoff = -1
    if hasattr(args, "co") and args.co:
        cutoff = int(args.co)
    if hasattr(args, "o") and args.o:
        offset = int(args.o)

        if offset == 0:
            print("Offset must be nonzero.")
        else:
            converter = Editor(
                captions_file=args.caption_filename,
                dest_filename=args.d,
                dest_directory=args.dd,
                dest_file_extensions=args.dt,
                offset=offset,
                cutoff=cutoff,
            )
            converter.edit_captions()
    else:
        converter = Editor(
            captions_file=args.caption_filename,
            conversions_file=args.c,
            dest_filename=args.d,
            dest_directory=args.dd,
            dest_file_extensions=args.dt,
            cutoff=cutoff,
        )
        converter.edit_captions()

    return args


if __name__ == "__main__":
    main()
