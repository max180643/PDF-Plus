# PDF-Plus

Automates PDF cropping using OCR to detect text regions and applies custom margins around the content

## Prerequisites

- Python 3.x
- pip (Python package installer)
- EasyOCR, OpenCV, PyMuPDF

## Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/max180643/PDF-Plus
cd PDF-Plus
```

#### 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

For macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Required Dependencies

Install the project dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

## Usage

1. Place the input PDF in the project folder and specify the path in the script (default: `input.pdf`)

2. Customize the configuration in the script:

   - Set margins: `margin_top`, `margin_bottom`, `margin_left`, `margin_right`
   - Enable or disable preview mode: `preview_mode = True/False`
   - Specify pages to skip: `ignore_pages = [list of page numbers]`
   - Choose whether to enable GPU for OCR: `gpu_enable = True/False`

3. Run the script:

```bash
python3 main.py
```

4. The processed, cropped PDF will be saved as `output.pdf`

## Preview Mode

#### Rectangle

- Green line: auto detect text regions
- Red line: crop regions with custom margins
