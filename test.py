# Automated Test Suite Generator
# A comprehensive testing framework for web applications with form validation and reporting

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import logging
import argparse

@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    url: str
    actions: List[Dict[str, Any]]
    expected_results: List[Dict[str, Any]]
    test_type: str = "functional"
    priority: str = "medium"
    tags: List[str] = None

@dataclass
class TestResult:
    """Represents test execution result"""
    test_name: str
    status: str  # PASS, FAIL, SKIP
    execution_time: float
    error_message: str = ""
    screenshot_path: str = ""
    timestamp: str = ""

class TestCaseGenerator:
    """Generates test cases for various scenarios"""
    
    @staticmethod
    def generate_form_validation_tests(form_config: Dict) -> List[TestCase]:
        """Generate comprehensive form validation test cases"""
        tests = []
        
        # Required field validation
        for field in form_config.get('required_fields', []):
            tests.append(TestCase(
                name=f"test_required_field_{field['name']}",
                url=form_config['url'],
                actions=[
                    {"action": "clear_field", "selector": field['selector']},
                    {"action": "click", "selector": form_config['submit_button']},
                ],
                expected_results=[
                    {"type": "element_visible", "selector": field.get('error_selector', f"#{field['name']}-error")}
                ],
                test_type="validation",
                tags=["form", "validation", "required"]
            ))
        
        # Data type validation
        for field in form_config.get('validation_fields', []):
            if field['type'] == 'email':
                tests.append(TestCase(
                    name=f"test_email_validation_{field['name']}",
                    url=form_config['url'],
                    actions=[
                        {"action": "input", "selector": field['selector'], "value": "invalid-email"},
                        {"action": "click", "selector": form_config['submit_button']},
                    ],
                    expected_results=[
                        {"type": "element_visible", "selector": field.get('error_selector', f"#{field['name']}-error")}
                    ],
                    test_type="validation",
                    tags=["form", "validation", "email"]
                ))
            
            elif field['type'] == 'phone':
                tests.append(TestCase(
                    name=f"test_phone_validation_{field['name']}",
                    url=form_config['url'],
                    actions=[
                        {"action": "input", "selector": field['selector'], "value": "123"},
                        {"action": "click", "selector": form_config['submit_button']},
                    ],
                    expected_results=[
                        {"type": "element_visible", "selector": field.get('error_selector', f"#{field['name']}-error")}
                    ],
                    test_type="validation",
                    tags=["form", "validation", "phone"]
                ))
        
        # Successful form submission
        valid_data = {field['name']: field.get('valid_value', 'test') 
                     for field in form_config.get('all_fields', [])}
        
        actions = [{"action": "input", "selector": field['selector'], "value": valid_data[field['name']]} 
                  for field in form_config.get('all_fields', [])]
        actions.append({"action": "click", "selector": form_config['submit_button']})
        
        tests.append(TestCase(
            name="test_successful_form_submission",
            url=form_config['url'],
            actions=actions,
            expected_results=[
                {"type": "url_contains", "value": form_config.get('success_url', '/success')}
            ],
            test_type="functional",
            tags=["form", "success"]
        ))
        
        return tests
    
    @staticmethod
    def generate_regression_tests(pages_config: List[Dict]) -> List[TestCase]:
        """Generate regression test cases for multiple pages"""
        tests = []
        
        for page in pages_config:
            # Page load test
            tests.append(TestCase(
                name=f"test_page_load_{page['name']}",
                url=page['url'],
                actions=[{"action": "wait", "time": 2}],
                expected_results=[
                    {"type": "title_contains", "value": page.get('expected_title', page['name'])}
                ],
                test_type="regression",
                tags=["page_load", "regression"]
            ))
            
            # Critical elements test
            if 'critical_elements' in page:
                tests.append(TestCase(
                    name=f"test_critical_elements_{page['name']}",
                    url=page['url'],
                    actions=[{"action": "wait", "time": 1}],
                    expected_results=[
                        {"type": "element_visible", "selector": selector} 
                        for selector in page['critical_elements']
                    ],
                    test_type="regression",
                    tags=["elements", "regression"]
                ))
        
        return tests

class TestExecutor:
    """Executes test cases using Selenium WebDriver"""
    
    def __init__(self, headless: bool = True, timeout: int = 10):
        self.timeout = timeout
        self.driver = None
        self.headless = headless
        self.results = []
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('test_execution.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Initialize WebDriver with appropriate options"""
        options = Options()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(self.timeout)
        return self.driver
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """Execute a single test action"""
        try:
            if action['action'] == 'input':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, action['selector']))
                )
                element.clear()
                element.send_keys(action['value'])
                
            elif action['action'] == 'click':
                element = WebDriverWait(self.driver, self.timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, action['selector']))
                )
                element.click()
                
            elif action['action'] == 'clear_field':
                element = self.driver.find_element(By.CSS_SELECTOR, action['selector'])
                element.clear()
                
            elif action['action'] == 'wait':
                time.sleep(action.get('time', 1))
                
            return True
            
        except Exception as e:
            self.logger.error(f"Action failed: {action} - {str(e)}")
            return False
    
    def verify_result(self, expected: Dict[str, Any]) -> bool:
        """Verify expected test result"""
        try:
            if expected['type'] == 'element_visible':
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, expected['selector']))
                )
                return True
                
            elif expected['type'] == 'element_not_visible':
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, expected['selector'])
                    return not element.is_displayed()
                except NoSuchElementException:
                    return True
                    
            elif expected['type'] == 'url_contains':
                return expected['value'] in self.driver.current_url
                
            elif expected['type'] == 'title_contains':
                return expected['value'].lower() in self.driver.title.lower()
                
            elif expected['type'] == 'text_contains':
                element = self.driver.find_element(By.CSS_SELECTOR, expected['selector'])
                return expected['value'] in element.text
                
            return False
            
        except Exception as e:
            self.logger.error(f"Verification failed: {expected} - {str(e)}")
            return False
    
    def take_screenshot(self, test_name: str) -> str:
        """Take screenshot for failed test"""
        try:
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{test_name}_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            self.driver.save_screenshot(filepath)
            return filepath
        except Exception as e:
            self.logger.error(f"Screenshot failed: {str(e)}")
            return ""
    
    def execute_test(self, test_case: TestCase) -> TestResult:
        """Execute a single test case"""
        start_time = time.time()
        result = TestResult(
            test_name=test_case.name,
            status="FAIL",
            execution_time=0,
            timestamp=datetime.now().isoformat()
        )
        
        try:
            self.logger.info(f"Executing test: {test_case.name}")
            
            # Navigate to URL
            self.driver.get(test_case.url)
            
            # Execute actions
            for action in test_case.actions:
                if not self.execute_action(action):
                    result.error_message = f"Action failed: {action}"
                    result.screenshot_path = self.take_screenshot(test_case.name)
                    return result
            
            # Verify results
            for expected in test_case.expected_results:
                if not self.verify_result(expected):
                    result.error_message = f"Verification failed: {expected}"
                    result.screenshot_path = self.take_screenshot(test_case.name)
                    return result
            
            result.status = "PASS"
            self.logger.info(f"Test passed: {test_case.name}")
            
        except Exception as e:
            result.error_message = str(e)
            result.screenshot_path = self.take_screenshot(test_case.name)
            self.logger.error(f"Test failed: {test_case.name} - {str(e)}")
        
        finally:
            result.execution_time = time.time() - start_time
        
        return result
    
    def execute_test_suite(self, test_cases: List[TestCase]) -> List[TestResult]:
        """Execute a complete test suite"""
        self.setup_driver()
        results = []
        
        try:
            for test_case in test_cases:
                result = self.execute_test(test_case)
                results.append(result)
                self.results.append(result)
                
                # Add small delay between tests
                time.sleep(1)
                
        finally:
            if self.driver:
                self.driver.quit()
        
        return results

class ReportGenerator:
    """Generates detailed test reports"""
    
    @staticmethod
    def generate_html_report(results: List[TestResult], output_file: str = "test_report.html"):
        """Generate comprehensive HTML report"""
        
        total_tests = len(results)
        passed_tests = len([r for r in results if r.status == "PASS"])
        failed_tests = len([r for r in results if r.status == "FAIL"])
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Execution Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
                .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
                .metric {{ text-align: center; padding: 10px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .status-pass {{ background-color: #d4edda; }}
                .status-fail {{ background-color: #f8d7da; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Automated Test Suite Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Total Tests</h3>
                    <h2>{total_tests}</h2>
                </div>
                <div class="metric">
                    <h3 class="pass">Passed</h3>
                    <h2 class="pass">{passed_tests}</h2>
                </div>
                <div class="metric">
                    <h3 class="fail">Failed</h3>
                    <h2 class="fail">{failed_tests}</h2>
                </div>
                <div class="metric">
                    <h3>Pass Rate</h3>
                    <h2>{pass_rate:.1f}%</h2>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Status</th>
                        <th>Execution Time (s)</th>
                        <th>Error Message</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for result in results:
            status_class = f"status-{result.status.lower()}"
            html_content += f"""
                    <tr class="{status_class}">
                        <td>{result.test_name}</td>
                        <td>{result.status}</td>
                        <td>{result.execution_time:.2f}</td>
                        <td>{result.error_message}</td>
                        <td>{result.timestamp}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        with open(output_file, 'w') as f:
            f.write(html_content)
        
        return output_file
    
    @staticmethod
    def generate_csv_report(results: List[TestResult], output_file: str = "test_results.csv"):
        """Generate CSV report for further analysis"""
        data = [asdict(result) for result in results]
        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        return output_file
    
    @staticmethod
    def generate_summary_stats(results: List[TestResult]) -> Dict[str, Any]:
        """Generate summary statistics"""
        if not results:
            return {}
        
        total_time = sum(r.execution_time for r in results)
        avg_time = total_time / len(results)
        
        stats = {
            "total_tests": len(results),
            "passed_tests": len([r for r in results if r.status == "PASS"]),
            "failed_tests": len([r for r in results if r.status == "FAIL"]),
            "total_execution_time": total_time,
            "average_execution_time": avg_time,
            "pass_rate": len([r for r in results if r.status == "PASS"]) / len(results) * 100
        }
        
        return stats

# Example usage and configuration
def main():
    """Main function demonstrating the test suite generator"""

    parser = argparse.ArgumentParser(description="Automated Test Suite Generator")
    parser.add_argument('--test-type', type=str, default='all', choices=['all', 'form', 'regression', 'performance', 'unit'], help='Type of test to run')
    args = parser.parse_args()

    # Read the URL from webtest_url.txt
    url_file = "webtest_url.txt"
    if not os.path.exists(url_file):
        print(f"URL file '{url_file}' not found.")
        return
    with open(url_file, "r") as f:
        user_url = f.read().strip()
    if not user_url:
        print("No URL provided in webtest_url.txt.")
        return

    # Use user-provided URL in form and regression test configs
    form_config = {
        "url": user_url,
        "submit_button": "#contact-form button[type='submit']",  # Update if your form uses a different selector
        "success_url": "/#contact",  # Update if your form redirects or shows a message
        "required_fields": [
            {"name": "name", "selector": "#name", "error_selector": ".name-error"},
            {"name": "email", "selector": "#email", "error_selector": ".email-error"},
            {"name": "message", "selector": "#message", "error_selector": ".message-error"}
        ],
        "validation_fields": [
            {"name": "email", "selector": "#email", "type": "email", "error_selector": ".email-error"}
        ],
        "all_fields": [
            {"name": "name", "selector": "#name", "valid_value": "John Doe"},
            {"name": "email", "selector": "#email", "valid_value": "john@example.com"},
            {"name": "message", "selector": "#message", "valid_value": "Hello!"}
        ]   
    }

    pages_config = [
        {
            "name": "user-page",
            "url": user_url,
            "expected_title": "",  # Optionally update if you want to check for a specific title
            "critical_elements": []
        }
    ]

    # Generate test cases
    generator = TestCaseGenerator()
    all_tests = []
    if args.test_type in ['all', 'form']:
        all_tests += generator.generate_form_validation_tests(form_config)
    if args.test_type in ['all', 'regression']:
        all_tests += generator.generate_regression_tests(pages_config)
    if args.test_type in ['all', 'performance']:
        # Placeholder: implement performance test generation if needed
        pass
    if args.test_type in ['all', 'unit']:
        # Placeholder: implement unit test generation if needed
        pass

    print(f"Generated {len(all_tests)} test cases for {user_url} [{args.test_type}]")

    # Execute tests
    executor = TestExecutor(headless=True)
    results = executor.execute_test_suite(all_tests)

    # Generate reports
    report_gen = ReportGenerator()
    html_report = report_gen.generate_html_report(results)
    csv_report = report_gen.generate_csv_report(results)
    stats = report_gen.generate_summary_stats(results)

    print(f"Test execution completed!")
    print(f"HTML Report: {html_report}")
    print(f"CSV Report: {csv_report}")
    print(f"Summary: {stats}")

if __name__ == "__main__":
    main()