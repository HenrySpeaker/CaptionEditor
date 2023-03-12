import webvtt
import argparse
from pathlib import Path
import json
import re
from flashtext import KeywordProcessor


class WebVTTConverter:
    def __init__(
        self,
        captions_file,
        conversions_file="conversions.json",
        dest_filename="",
        offset=0,
        cutoff=-1,
    ):
        self._captions_file_path = None
        self.conversions_file_path = None
        self.new_captions_path = None

        # Set captions path
        self.update_captions_path(captions_file)

        # Update or create file path for converted captions
        self.update_dest_captions_file(dest_filename)

        self.timing_offset = offset

        self.conversions = []

        self._case_sensitive_processor = KeywordProcessor(case_sensitive=True)
        self._case_insensitive_processor = KeywordProcessor()
        self._previous_caption_keys_processor = KeywordProcessor()
        self._previous_caption_keys = []
        self._previous_captions_processors = {}
        self._direct_conversions = {}

        # If no offset value was provided or if it was zero, check for and process a conversions file
        if offset == 0:
            self.update_conversions(conversions_file)

        self.update_cutoff(cutoff)

    def _store_conversions(self):
        """
        Store conversions file data.
        """

        with open(self.conversions_file_path) as conversions_json:
            conversions_data = json.load(conversions_json)

        # Verify that the structure of the file matches what's expected
        if len(conversions_data) > 2 or any(
            key not in ("offset", "conversions") for key in conversions_data.keys()
        ):
            raise ValueError("Invalid conversions.json contents")

        self.timing_offset = conversions_data["offset"]
        self.conversions = conversions_data["conversions"]

    def _process_caption_contents(self, caption_text=""):
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

    def _create_new_dest_path(self):
        """
        If there is no name or no appropriate name for the destination file, a name will be created based on the original file, with '-converted' appended to the filename's stem.
        """

        # Add '-converted' to the end of the stem of the current caption file path so the converted captions are distinguished from the original
        original_name = self._captions_file_path.stem
        self.new_captions_path = Path(self._captions_file_path).with_stem(
            original_name + "-converted"
        )

    def _build_keyword_processors(self):
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

        for conversion in self.conversions:
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

    def update_cutoff(self, new_cutoff):
        """
        Updates the time cutoff (in seconds) for captions to be written. Any captions, after the offset has been applied, that would occur after the cutoff will not be included.
        """
        self.cutoff = new_cutoff

    def update_captions_path(self, captions_file):
        """
        Check if provided file path is a valid vtt file, update the file path property if it is, and raise an error if not.
        """

        self._captions_file_path = Path(captions_file)
        if (
            not self._captions_file_path.is_file()
            or self._captions_file_path.suffix != ".vtt"
        ):
            self._captions_file_path = None
            raise FileNotFoundError("Captions file not found")

    def update_conversions(self, conversions):
        """
        Check if conversions file exists and process its contents.
        """

        self.conversions_file_path = Path(conversions)
        if (
            not self.conversions_file_path.is_file()
            or self.conversions_file_path.suffix != ".json"
        ):
            self.conversions_file_path = None
            raise FileNotFoundError("Conversions file not found")
        self._store_conversions()
        self._build_keyword_processors()

    def update_dest_captions_file(self, new_name=""):
        """
        Check for valid filename for output file and create one if necessary. If no filename, a non-vtt filename, or the same filename as the original captions file is entered a new filename will be created.
        """

        if new_name:
            new_filename_path = Path(new_name)
            if (
                new_filename_path.suffix != ".vtt"
                or new_filename_path == self._captions_file_path
            ):
                self._create_new_dest_path()
            else:
                self.new_captions_path = new_filename_path
        else:
            self._create_new_dest_path()

    def convert_captions(self):
        """
        Reads captions from captions file, converts them based on offset and conversions file, and writes them to the destination file.
        """

        pattern = re.compile(r"(\d{2,}):(\d\d):(\d\d).(\d\d\d)")

        def offset_time(time):
            time_info = pattern.search(time).groups()
            hours = int(time_info[0])
            minutes = int(time_info[1])
            seconds = int(time_info[2])
            milliseconds = int(time_info[3]) + self.timing_offset

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

            # since negative timestamps aren't valid in WebVTT, None is returned to signal that the current caption should not be included in the new file
            if min(hours, minutes, seconds, milliseconds) < 0:
                return (None, 0)

            new_time = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}.{str(milliseconds).zfill(3)}"
            return (
                new_time,
                hours * 3600 + minutes * 60 + seconds + milliseconds / 1000,
            )

        new_file_contents = "WEBVTT - Converted from " + str(self._captions_file_path)
        caption_count = 0

        for caption in webvtt.read(self._captions_file_path):
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

        with open(self.new_captions_path, "w", encoding="utf8") as new_captions_file:
            new_captions_file.write(new_file_contents)


def main(args=None):
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
    args = parser.parse_args(args)
    if hasattr(args, "o") and args.o:
        offset = int(args.o)
        if offset == 0:
            print("Offset must be nonzero.")
        else:
            converter = WebVTTConverter(
                captions_file=args.caption_filename, dest_filename=args.d, offset=offset
            )
    else:
        converter = WebVTTConverter(
            captions_file=args.caption_filename,
            conversions_file=args.c,
            dest_filename=args.d,
        )
        converter.convert_captions()

    return args


if __name__ == "__main__":
    main()
