import webvtt
import argparse
from pathlib import Path
import json


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

        conversions_data = json.load(self.conversions_file)

        if len(conversions_data) > 2 or any(
            key not in ("offset", "conversions") for key in conversions_data.keys()
        ):
            return

        self.timing_offset = conversions_data["offset"]
        self.conversions = conversions_data["conversions"]

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

        self._store_conversions()

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
            # check if vtt file exists in specified directory

            # check if requirements file exists in specified directory

            # process conversions and store them in appropriate data structure

            # note: if offset causes a caption to start with a negative timestamp it shouldn't be included in the new captions file

            # open the file and process each caption, storing the results in a new object

            # create a new file and put modified contents in that file

            pass


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
    )
    args = parser.parse_args()
    if hasattr(args, "o"):
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
    print(args.caption_filename, args.c, args.d)
