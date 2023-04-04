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



### Using the command line

