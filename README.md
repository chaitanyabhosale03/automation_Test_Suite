# Automated Test Suite Generator

This project provides a web-based interface and a Python backend for automated testing of web applications. It supports form validation, regression, performance, and unit testing using Selenium and Flask.

## Features
- Web UI to trigger tests and view reports
- Supports multiple test types: Form Validation, Regression, Performance, Unit
- Generates HTML and CSV reports
- Screenshot capture on failure

---

## Setup Instructions

### 1. Clone the Repository
```
git clone <your-repo-url>
cd Automated Test Suite Generator
```

### 2. Create and Activate a Virtual Environment
```
python -m venv myenv
# On Windows:
myenv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. (Optional) Install ChromeDriver
- Download the ChromeDriver matching your Chrome version from https://chromedriver.chromium.org/downloads
- Place it in your PATH or the project directory

---

## Usage

### 1. Start the Web Interface
```
python web_tester.py
```
- Open your browser and go to `http://127.0.0.1:5000/`

### 2. Run a Test
- Enter the website URL you want to test.
- Select the type of test (All, Form Validation, Regression, Performance, Unit).
- Click "Run Test".
- After the test completes, click "View Report" to see the results.

### 3. View Reports
- `test_report.html`: Detailed HTML report with results and errors
- `test_results.csv`: CSV report for further analysis
- `screenshots/`: Folder containing screenshots of failed tests

---

## How It Works

- **web_tester.py**: Flask app providing the web UI. Takes user input, writes the URL to `webtest_url.txt`, and runs `test.py` with the selected test type.
- **test.py**: Main test runner. Reads the URL and test type, generates and runs the appropriate tests, and creates reports.
- **testv0.1.py**: (Optional) Enhanced/experimental version with more advanced features and reporting.

---

## Customization
- To test different forms or websites, update the selectors in `test.py` or make the form configuration dynamic.
- To add new test types (e.g., performance, unit), implement the corresponding test case generators in `test.py`.

---

## Troubleshooting
- **Selenium errors**: Ensure ChromeDriver is installed and matches your Chrome version.
- **ModuleNotFoundError**: Make sure you are using the correct virtual environment (`myenv`).
- **Form tests fail**: Update the form selectors in `test.py` to match your target website.

---
<<<<<<< HEAD
=======

## License
MIT
>>>>>>> 8f9b459 (Initial commit: Automation Test Suite Generator)
