# CaptionEditor
![python version](https://img.shields.io/badge/python-3.10%2B-blue) ![license](https://img.shields.io/badge/license-MIT-green)
## Project Description
CaptionEditor helps you modify the contents of the captions files and convert captions between common caption filetypes. You can replace words and phrases inside of caption text as well as modify the timing of captions. 

The package uses [pycaption](https://pypi.org/project/pycaption/) to convert caption files to other caption filetypes, [webvtt-py](https://pypi.org/project/webvtt-py/) to parse the captions for editing, and [flashtext2](https://pypi.org/project/flashtext2/) to replace the words and phrases with corrections in each caption.


You are free to copy, modify, and distribute CaptionEditor with attribution under the terms of the MIT license.

## Table of contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
    - [Editor class](#the-editor-class)
        - [Initializing the Editor class](#initializing-the-editor-class)
        - [Editor class methods](#editor-class-methods)
        - [Editor class example](#editor-class-example)
    - [CaptionEditor command line instructions](#captioneditor-command-line-instructions)
        - [Command line example](#command-line-example)
    - [Setting up the conversions JSON file](#setting-up-the-conversions-json-file) 


## Prerequisites
CaptionEditor requires [Python 3.10+](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/).

## Installation
Use pip to install CaptionEditor

```bash
pip install captioneditor
```

## Usage
The package contains one class: Editor.

This class can be imported and used in a python file or conversions can be initiated from the command line.


### The Editor class
#### Initializing the Editor class
The Editor class accepts a number of parameters:
- captions_file: (Required) A Path object or the string of a path that points to the initial captions file.

- conversions_file: A Path object or the string of a path that points to the conversions JSON file. Instructions are available [here](#setting-up-the-conversions-json-file) for constructing a conversions JSON file. If no conversions file is found, the Editor will look for a file called "conversions.json" in the current directory.

- dest_filename: An optional string that specifies the stem of any new caption files that are created. If no name is supplied, the default name for any new captions files will be &lt;captions file stem&gt;-converted.&lt;extension&gt;

- dest_file_extensions: A list or tuple that contains the strings of the filetype extensions the captions should be converted to. The list or tuple should only contain the following strings: ".dfxp", ".srt", ".ttml", and ".vtt".

- dest_directory: A Path object or string of a path that points to the directory where the converted captions should be written.

- offset: An integer, in milliseconds, that measures the timing offset for each caption. A positive value increases the timestamp for each caption's start and end by the specified number of milliseconds, and a negative offset decreases the timestamp by the specified number of milliseconds. If the offset would cause a timestamp to become negative, the caption which the timestamp belongs to will not be included in the conversions. 

    NOTE: if a non-zero offset value is provided, it is assumed that no additional conversions (with the exception of an optional cutoff) is desired and the contents of the conversions file will not automatically be stored. If the user wishes to pass in a non-zero offset *and* use the conversions file, the method Editor.update_conversions(*conversions_file*) can be used to store the contents of the conversions file after the converter has been initialized.

- cutoff: An integer, in seconds. Any caption that starts after the number of seconds specified by the cutoff has passed will not be included in the conversions.

#### Editor class methods
- edit_captions(): This implements the edits and conversions. New files of the specified filetypes that contain the specified edits will be written to the destination directory (or the current director if no destination directory was provided).

- update_captions_path(*captions_file*): Stores the supplied Path object or the string of a path that points to the new initial captions file.

- update_conversions(*conversions*): Stores the supplied Path object or the string of a path that points to the conversions JSON file.

- update_dest_filename(*new_name*): Stores the supplied filename string. All files produced by running Editor.edit_captions() will have the given filename.

- update_dest_directory(*new_directory*): Stores the supplied Path object or the string of a path that points to the new destination directory. All files produced by running Editor.edit_captions() will appear in the given directory.

- update_cutoff(*new_cutoff*): Stores the supplied integer or float. If *new_cutoff* is greater than zero, any new caption files that would be produced by running Editor.edit_captions() will be cut off after the number of seconds equal to *new_cutoff*.

#### Editor class example

```python
from captioneditor import Editor
import os

editor = Editor(
    captions_file="my_captions.vtt",
    conversions_file="conversion/conversions2.json",
    dest_filename="my-new-captions",
    dest_file_extensions=[".dfxp", ".srt", ".ttml", ".vtt"],
    dest_directory=Path(os.getcwd()) / "new-captions",
)

editor.edit_captions()
```

---

### CaptionEditor command line instructions
Format: 
```bash
edit-captions <captions file> 
              [-c <conversions file>]
              [-n <new file name>]
              [-dd <destination directory>]
              [-dt <file extension 1> <file extension 2> ...]
              [-o <offset value>]
              [-co <cutoff value>]
```

The command accepts one required positional argument: &lt;captions file&gt;

There are a number of optional arguments:
- -c or -conversions: The JSON conversions file that follows the [required format](#setting-up-the-conversions-json-file).
- -n or -name: The name for the converted caption files.
- -dd or -dest_dir: The path to the directory where the converted caption file should be written.
- -dt or -dest_types: Any combination of valid file extensions representing the desired filetypes of the converted captions. The valid file extensions are: .dfxp, .srt, .ttml, .vtt.
- -o or -offset: An offset integer (in ms) for the converter. A negative value will make each caption appear earlier by the specified number of milliseconds and a positive value will make them appear later. **NOTE:** If this is supplied, no conversions will be used from a .json file and only the offset will be applied.
- -co or -cutoff: An integer (in seconds) that specifies the timestamp after which no more captions should occur. 

#### Command line example
```bash
edit-captions my_captions.srt -c conversions2.json -n my_converted_captions -dd converted-captions -dt .srt .vtt .dfxp
```

---

### Setting up the conversions JSON file
The conversions file will contain the text conversions to be applied, as well as optional offset and cutoff values.

A negative offset value will make each caption appear earlier by the specified number of milliseconds and a positive value will make them appear later. If an offset value is not included, no offset will be applied. 

A negative cutoff value will not cut off any captions, but a zero or positive cutoff value will cut off captions after the specified number of seconds. If a cutoff value is not included, no cutoff will be applied.

The conversions file must be a JSON file. This is an example that demonstrates the structure:
```
{
    "offset": 10000,
    "cutoff": -1, 
    "conversions": [
        {
            "key": "dlrow olleh",
            "replacement": "hello world",
            "caseSensitive": true
        },
        {
            "key": "alright",
            "replacement": "all right",
            "previous": null,
            
        },
        {
            "key": "five",
            "replacement": "5,",
            "directConversion": true
        }
    ]
}
```

Each element in the conversions array must contain the "key" and "replacement" properties, and can optionally contain the "previous", "caseSensitive", and "directConversion" properties.

- "key": This must have a string value paired with it. The string will be used to match text in the captions.

- "replacement": This must have a string value paired with it. The string will replace any instance of the key string matched in the captions.

- "previous": This is an optional property that, if included, must be paired with a string. If the "previous" property is included in an element, then the "replacement" value will only be used when the "key" value is found in a particular caption *and* the "previous" value was found anywhere in the previous caption. If this property is included in an element, it will override the "caseSensitive" and "directConversion" properties if they've been included.

    Note: If the "previous" property is included, both the "key" and "previous" values will have case-sensitive matching.

- "caseSensitive": This is an optional property that, if included, must be paired with a boolean. If the value associated with this property is true, then the "key" value must make a case-sensitive match inside of the current caption for the "key" value's text to be replaced.

- "directConversion": This is an optional property that, if included, must be paired with a string. If an entire caption makes a case-sensitive match with the "directConversion" value, then the entire caption will be replaced with the "replacement" value. If this is included in an element, it will override the "key" and "caseSensitive" values.


Note: if two elements contain the same key, but one is case-sensitive and the other is not, the case-sensitive replacement will supersede the case-insensitive replacement.

Note: if two elements contain the same key and case-sensitivity but have different replacement values, there is no guarantee as to which replacement will be the one that takes effect.


