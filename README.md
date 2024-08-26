# Insurance
Insurance Project for HyperGAI Insurance Project POC
# Project Title

This project processes images and PDF files to extract structured data and provides a Streamlit interface for user interaction. The project also includes image preprocessing for enhanced image quality.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Streamlit Interface](#streamlit-interface)
- [License](#license)

## Introduction

This project is designed to process images and PDF files, extract structured data, and provide a user-friendly interface via Streamlit. It includes preprocessing steps to enhance image quality for better accuracy in data extraction. The project supports the analysis of two types of data:
1. Medical Reports
2. Invoices and Receipts

## Installation

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- Required libraries listed in `requirements.txt`

## Configuration

Before running the project, configure the necessary settings:

1. Set up your environment variables and configurations in `my_config.py`.

## Usage

To start the application, use the following command for the respective data types:

### Medical Reports

```bash
streamlit run Medical_Report/main.py
```

### Invoices and Receipts

```bash
streamlit run Invoices_receipts/Invoice_Recipes_Demo.py
```

## Streamlit Interface

The Streamlit interface allows users to upload images and PDF files, which are then processed to extract structured data. Follow these steps to use the interface:

1. Launch the Streamlit interface using the appropriate command above.
2. Upload an image or PDF file.
3. View the extracted data in the output section.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
