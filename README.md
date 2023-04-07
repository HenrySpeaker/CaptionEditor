# Caption Converter

## Project Description
I created this package after spending significant amounts of time manually correcting the same typos in caption files. The repetitive work seemed like a good candidate for automation so the project was initially built to parse captions and replace common typos with corrections. After that functionality was built the option to convert captions to various common caption filetypes was added.

The package uses [pycaption](https://pypi.org/project/pycaption/) to convert caption files to other caption filetypes, [webvtt-py](https://pypi.org/project/webvtt-py/) to parse the captions, and [flashtext2](https://pypi.org/project/flashtext2/) to replace the typos with corrections in each caption.

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
- dest_file_extensions:
- dest_directory:
- offset:
- cutoff:

#### Setting up the conversions JSON file
The conversions file will contain the


### Using the command line

