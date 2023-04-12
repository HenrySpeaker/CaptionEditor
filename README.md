# CaptionConverter

## Project Description
CaptionConverter helps you convert captions between common caption filetypes as well as modify the contents of the captions files themselves. You can replace words and phrases inside of caption text as well as modify the timing of captions. 

I created this package after spending significant amounts of time manually correcting the same typos in caption files. The repetitive work seemed like a good candidate for automation so the project was initially built to parse captions and replace common typos with corrections. After that functionality was built the option to convert captions to various common caption filetypes was added.

The package uses [pycaption](https://pypi.org/project/pycaption/) to convert caption files to other caption filetypes, [webvtt-py](https://pypi.org/project/webvtt-py/) to parse the captions, and [flashtext2](https://pypi.org/project/flashtext2/) to replace the words and phrases with corrections in each caption.


You are free to copy, modify, and distribute CaptionConverter with attribution under the terms of the MIT license.

## Prerequisites
CaptionConverter requires [Python 3.10+](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installation/).

## Installation
Use pip to install CaptionConverter

```bash
pip install captionconverter
```

## Usage
The package contains one class: CaptionConverter.

This class can be imported and used in a python file or conversions can be initiated from the command line.



### Using the CaptionConverter class
The CaptionConverter class accepts a number of parameters:
- captions_file: A Path object or the string of a path that points to the original captions file.
- conversions_file: A Path object or the string of a path that points to the conversions JSON file. Instructions are available [here](#setting-up-the-conversions-json-file) for constructing a conversions JSON file.

- dest_filename: An optional string that specifies the stem of any new caption files that are created. If no name is supplied, the default name for any new captions files will be &lt;captions file stem&gt;-converted.&lt;extension&gt;

- dest_file_extensions: A list or tuple that contains the strings of the filetype extensions the captions should be converted to. The list or tuple should only contain the following strings: ".dfxp", ".srt", ".ttml", and ".vtt".

- dest_directory: A Path object or string of a path that points to the directory where the converted captions should be written.

- offset: An integer, in milliseconds, that measures the timing offset for each caption. A positive value increases the timestamp for each caption's start and end by the specified number of milliseconds, and a negative offset decreases the timestamp by the specified number of milliseconds. If the offset would cause a timestamp to become negative, the caption which the timestamp belongs to will not be included in the conversions. 

    NOTE: if a non-zero offset value is provided, it is assumed that no additional conversions (with the exception of an optional cutoff) is desired and the contents of the conversions file will not automatically be stored. If the user wishes to pass in a non-zero offset *and* use the conversions file, the method CaptionConverter.update_conversions(*conversions_file*) can be used to store the contents of the conversions file after the converter has been initialized.

- cutoff: An integer, in seconds. Any caption that starts after the number of seconds specified by the cutoff has passed will not be included in the conversions.

#### Setting up the conversions JSON file
The conversions file will contain the text conversions to be applied, as well as optional offset and cutoff values. If an offset value is not included, no offset will be applied. If a cutoff value is not included, no cutoff will be applied.

Note: A negative cutoff value will not cut off any captions, but a zero or positive cutoff value will cut off captions after the specified number of seconds.

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

- "directConversion": This is an optional property that, if included, must be paired with a string. If an entire caption makes a case-sensitive match with the "directConversion" value, then the entire caption will be replaced with the "replacement" value. If this is included in an element, it will override the "key" and "caseSenstive" values.


Note: if two elements contain the same key, but one is case-sensitive and the other is not, the case-sensitive replacement will supersede the case-insensitive replacement.

Note: if two elements contain the same key and case-sensitivity but have different replacement values, there is no guarantee as to which replacement will be the one that takes effect.


### Using the command line

