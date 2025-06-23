from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
import subprocess
import os
import time

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Automated Web Tester</title>
</head>
<body>
    <h1>Automated Web Tester</h1>
    <form method="post">
        <label>Website URL:</label>
        <input type="text" name="url" style="width:400px" required>
        <label style='margin-left:20px;'>Test Type:</label>
        <select name="test_type">
            <option value="all">All</option>
            <option value="form">Form Validation</option>
            <option value="regression">Regression</option>
            <option value="performance">Performance</option>
            <option value="unit">Unit</option>
        </select>
        <button type="submit">Run Test</button>
    </form>
    {% if report_link %}
        <p>Test complete! <a href="{{ report_link }}" target="_blank">View Report</a></p>
    {% endif %}
</body>
</html>
"""

@app.route("/report")
def report():
    # Serve the test_report.html file from the current directory
    return send_from_directory('.', 'test_report.html')

@app.route("/", methods=["GET", "POST"])
def index():
    report_link = None
    if request.method == "POST":
        url = request.form["url"]
        test_type = request.form.get("test_type", "all")
        with open("webtest_url.txt", "w") as f:
            f.write(url)
        python_exe = os.path.join(os.getcwd(), "myenv", "Scripts", "python.exe")
        subprocess.run([python_exe, "test.py", "--test-type", test_type])
        if os.path.exists("test_report.html"):
            # Add a timestamp to the report link to prevent caching
            report_link = url_for('report') + f'?t={int(time.time())}'
    return render_template_string(HTML_FORM, report_link=report_link)

if __name__ == "__main__":
    app.run(debug=True)