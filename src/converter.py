import webvtt
import argparse
from pathlib import Path
import json
from datetime import datetime, timedelta
import re


class WebVTTConverter:
    def __init__(
        self,
        captions_file,
        conversions_file="conversions.json",
        dest_filename="",
        offset=0,
    ):
        self.captions_file_path = None
        self.conversions_file = None
        self.new_captions_path = None

        # set captions path
        self.update_captions_path(captions_file)

        # update or create file path for converted captions
        self.update_dest_captions_file(dest_filename)

        self.timing_offset = offset

        self.conversions = []

        if offset == 0:
            self.update_conversions(conversions_file)

    def _store_conversions(self):
        """
        Store conversions file data.
        """

        if not self.conversions_file:
            return

        with open(self.conversions_file) as conversions_json:
            conversions_data = json.load(conversions_json)

        if len(conversions_data) > 2 or any(
            key not in ("offset", "conversions") for key in conversions_data.keys()
        ):
            raise FileNotFoundError

        self.timing_offset = conversions_data["offset"]
        self.conversions = conversions_data["conversions"]

        print(self.timing_offset)
        print(self.conversions)

    def _process_caption(self, caption_text=""):
        pass

    def _create_new_dest_path(self):
        """
        If there is no name or no appropriate name for the destination file, a name will be created based on the original file, with '-converted' appended to the filename's stem.
        """
        original_name = self.captions_file_path.stem

        self.new_captions_path = Path(self.captions_file_path).with_stem(
            original_name + "-converted"
        )
        print(
            f"new destination file is: {self.new_captions_path} original file is: {self.captions_file_path}"
        )

    def update_captions_path(self, captions_file):
        """
        Check if provided file path is a valid vtt file, update the file path property if it is, and raise an error if not.
        """
        self.captions_file_path = Path(captions_file)
        if (
            not self.captions_file_path.is_file()
            or self.captions_file_path.suffix != ".vtt"
        ):
            self.captions_file_path = None
            raise FileNotFoundError("Captions file not found")

        # self._store_conversions()

    def update_conversions(self, conversions):
        """
        Check if conversions file exists and process its contents.
        """
        self.conversions_file = Path(conversions)
        if (
            not self.conversions_file.is_file()
            or self.conversions_file.suffix != ".json"
        ):
            self.conversions_file = None
            raise FileNotFoundError("Conversions file not found")
        self._store_conversions()

    def update_dest_captions_file(self, new_name=""):
        """
        Check for valid filename for output file and create one if necessary. If no filename, a non-vtt filename, or the same filename as the original captions file is entered a new filename will be created.
        """
        if new_name:
            new_filename_path = Path(new_name)
            if (
                not new_filename_path.is_file()
                or new_filename_path.suffix != ".vtt"
                or new_filename_path == self.captions_file_path
            ):
                self._create_new_dest_path()
            self.new_captions_path = new_name
        else:
            self._create_new_dest_path()

    def convert(self):
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

            # make sure an invalid time is not submitted
            if min(hours, minutes, seconds, milliseconds) < 0:
                return None

            new_time = f"{str(hours).zfill(2)}:{str(minutes).zfill(2)}:{str(seconds).zfill(2)}.{str(milliseconds).zfill(3)}"
            return new_time

        # open the file and process each caption, storing the results in a new object
        for caption in webvtt.read(self.captions_file_path):
            start_time = caption.start
            new_start = offset_time(start_time)
            print(f"original start time {start_time}. new start time {new_start}")
            # note: if offset causes a caption to start with a negative timestamp it shouldn't be included in the new captions file

        # create a new file and put modified contents in that file


if __name__ == "__main__":
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
    args = parser.parse_args()
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
            captions_file=args.caption_filename, conversions_file=args.c
        )
        converter.convert()
    # print(args.caption_filename, args.c, args.d)
