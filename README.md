# OCR and Data Extraction from PDF

## Overview

This Python script extracts text data from PDF files by converting them into images and then using Optical Character Recognition (OCR) with `pytesseract`. The script is particularly designed to process historical documents that contain names and places in a two-column format.

## Features

- Extracts the number of pages in a PDF.
- Converts PDF pages into images using `pdf2image`.
- Detects two-column text formatting in images.
- Uses OCR (`pytesseract`) to extract text from images.
- Processes extracted text into structured tabular data.
- Saves the extracted data into CSV files.
- Supports human-verified page ranges for improved accuracy.

## Prerequisites

Ensure you have the following dependencies installed:

```sh
pip install pytesseract pillow pandas pdf2image PyPDF2
```

Additionally, you need to install `Tesseract-OCR`. You can download it from:

- Windows: [Tesseract GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux/macOS: Install via package manager (`sudo apt install tesseract-ocr` or `brew install tesseract`)

## Usage

### 1. Extract Number of Pages from PDF

```python
num_pages = extarct_number_of_pdf_pages('path/to/pdf')
print(f'Total Pages: {num_pages}')
```

### 2. Convert PDF to Images

```python
convert_pdf_to_image('path/to/pdf', start_page=1, end_page=10)
```

This saves images of the specified pages in a folder.

### 3. Convert Images to DataFrame

```python
convert_images_to_dataframe('path/to/image/folder')
```

This extracts names and places from images and saves them as a CSV file.

### 4. Process Verified Page Ranges

If human-verified page ranges are available:

```python
page_ranges = create_page_range_from_txt_file('pdf_filename')
book_df = convert_page_range_to_dataframes('pdf_filename', page_ranges)
```

This improves data accuracy.

## Logging

The script logs errors and processing details to `output.log` to help with debugging.

## File Structure

```
project-folder/
│── books/
│   ├── example.pdf
│   ├── example_folder/
│   │   ├── page_1.jpg
│   │   ├── page_2.jpg
│── script.py
│── output.log
│── extracted_data.csv
```

## Author

Mahyar Rezazadeh

## License

This project is licensed under the MIT License.
