import webvtt
import argparse
from pathlib import Path


class Converter:
    def __init__(self, captions, conversions_file="conversions.txt", dest_filename=""):
        # set captions path
        self.update_captions_path(captions)

        # set conversions path and store them
        self.update_conversions(conversions_file)

        # update or create file path for converted captions
        self.update_dest_captions_file(dest_filename)

        self.timing_offset = 0

        self.conversions = []

        self._store_conversions()

    def _store_conversions(self):
        with open(self.conversions_file) as conv_file:
            for line in conv_file:
                print(f"conversions line is: {line}")

    def _process_caption(self, caption_text=""):
        pass

    def _create_new_filename(self):
        """
        If there is no name or no appropriate name for the destination file, a name will be created based on the original file, with '-converted' appended to the filename's stem
        """
        original_name = self.captions_file_path.stem

        self.new_filename = Path(self.captions_file_path).with_stem(
            original_name + "-converted"
        )
        print(
            f"new destination file is: {self.new_filename} original file is: {self.captions_file_path}"
        )

    def update_captions_path(self, captions_file):
        """
        Check if provided file path is a valid vtt file, update the file path property if it is, and raise an error if not
        """
        self.captions_file_path = Path(captions_file)
        if (
            not self.captions_file_path.is_file()
            or self.captions_file_path.suffix != ".vtt"
        ):
            raise FileNotFoundError("Captions file not found")

    def update_conversions(self, conversions):
        """
        check if conversions file exists and process its contents
        """
        self.conversions_file = Path(conversions)
        if (
            not self.conversions_file.is_file()
            or self.conversions_file.suffix != ".txt"
        ):
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
                self._create_new_filename()
            self.new_filename = new_name
        else:
            self._create_new_filename()

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
        default="conversions.txt",
        required=False,
        help="the text file containing the conversion rules",
    )
    parser.add_argument(
        "-d",
        "-destination",
        help="optional destination filename, default is '<previous filename>-converted.vtt'",
    )
    args = parser.parse_args()
    print(args.caption_filename, args.c, args.d)
    converter = Converter(args.caption_filename, args.c)
