"""
Generate comprehensive test report from pytest JSON output
"""

import json
import sys
from datetime import datetime
from typing import Dict, List, Any

def generate_markdown_report(json_file: str) -> str:
    """Generate markdown report from pytest JSON"""
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Extract summary
    summary = data.get('summary', {})
    tests = data.get('tests', [])
    
    total = summary.get('total', 0)
    passed = summary.get('passed', 0)
    failed = summary.get('failed', 0)
    skipped = summary.get('skipped', 0)
    duration = data.get('duration', 0)
    
    # Calculate pass rate
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Determine status emoji
    if failed == 0:
        status_emoji = "✅"
        status_text = "ALL TESTS PASSED"
    else:
        status_emoji = "❌"
        status_text = f"{failed} TEST(S) FAILED"
    
    # Build report
    report = f"""# {status_emoji} Test Report - {status_text}

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {total} |
| **✅ Passed** | {passed} |
| **❌ Failed** | {failed} |
| **⏭️  Skipped** | {skipped} |
| **Pass Rate** | {pass_rate:.1f}% |
| **Duration** | {duration:.2f}s |
| **Timestamp** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |

"""
    
    # Add failed tests details
    if failed > 0:
        report += "\n## ❌ Failed Tests\n\n"
        for test in tests:
            if test.get('outcome') == 'failed':
                test_name = test.get('nodeid', 'Unknown')
                error_msg = test.get('call', {}).get('longrepr', 'No error message')
                
                report += f"### `{test_name}`\n\n"
                report += f"```\n{error_msg}\n```\n\n"
    
    # Add passed tests summary
    if passed > 0:
        report += f"\n## ✅ Passed Tests ({passed})\n\n"
        for test in tests:
            if test.get('outcome') == 'passed':
                test_name = test.get('nodeid', 'Unknown').split('::')[-1]
                duration = test.get('call', {}).get('duration', 0)
                report += f"- ✅ `{test_name}` ({duration:.2f}s)\n"
    
    # Add performance warnings
    slow_tests = [t for t in tests if t.get('call', {}).get('duration', 0) > 5.0]
    if slow_tests:
        report += "\n## ⚠️  Slow Tests (>5s)\n\n"
        for test in slow_tests:
            test_name = test.get('nodeid', 'Unknown').split('::')[-1]
            duration = test.get('call', {}).get('duration', 0)
            report += f"- ⏱️  `{test_name}` ({duration:.2f}s)\n"
    
    # Add recommendations
    if failed > 0:
        report += "\n## 🔧 Recommendations\n\n"
        report += "1. Review failed test logs above\n"
        report += "2. Check for environment/configuration issues\n"
        report += "3. Verify test data and expected outcomes\n"
        report += "4. Run tests locally to reproduce\n"
        report += "5. Fix issues before merging\n"
    
    # Add deployment status
    report += "\n## 🚀 Deployment Status\n\n"
    if failed == 0:
        report += "✅ **READY FOR DEPLOYMENT** - All tests passed\n"
    else:
        report += f"🚫 **DEPLOYMENT BLOCKED** - {failed} test(s) must be fixed\n"
    
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_test_report.py <json_report_file>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    try:
        report = generate_markdown_report(json_file)
        print(report)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{json_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


