#!/usr/bin/env python3
"""
Fetch and analyze Cloud Run logs
Provides error pattern detection and monitoring
"""
import subprocess
import json
import re
from collections import defaultdict
from datetime import datetime

def fetch_logs(limit=100):
    """Fetch recent logs from Cloud Run"""
    cmd = [
        "gcloud", "run", "services", "logs", "read",
        "aiproductivity-backend",
        "--region", "us-central1",
        "--project", "productivityai-mvp",
        "--limit", str(limit),
        "--format", "json"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logs = json.loads(result.stdout) if result.stdout else []
        return logs
    except subprocess.CalledProcessError as e:
        print(f"❌ Error fetching logs: {e.stderr}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing logs: {e}")
        return []


def analyze_logs(logs):
    """Analyze logs for errors and patterns"""
    errors = []
    warnings = []
    info = []
    error_patterns = defaultdict(int)
    endpoint_stats = defaultdict(lambda: {"count": 0, "errors": 0})
    
    for log in logs:
        severity = log.get("severity", "INFO")
        text = log.get("textPayload", "")
        timestamp = log.get("timestamp", "")
        
        # Categorize by severity
        if severity in ["ERROR", "CRITICAL"]:
            errors.append({"timestamp": timestamp, "message": text})
            
            # Extract error patterns
            if "Exception" in text:
                match = re.search(r'(\w+Exception)', text)
                if match:
                    error_patterns[match.group(1)] += 1
            elif "Error" in text:
                match = re.search(r'(\w+Error)', text)
                if match:
                    error_patterns[match.group(1)] += 1
        
        elif severity == "WARNING":
            warnings.append({"timestamp": timestamp, "message": text})
        else:
            info.append({"timestamp": timestamp, "message": text})
        
        # Extract endpoint stats
        endpoint_match = re.search(r'(GET|POST|PUT|DELETE|PATCH) (/[\w/\-]+)', text)
        if endpoint_match:
            method, path = endpoint_match.groups()
            endpoint = f"{method} {path}"
            endpoint_stats[endpoint]["count"] += 1
            if severity in ["ERROR", "CRITICAL"]:
                endpoint_stats[endpoint]["errors"] += 1
    
    return {
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "error_patterns": dict(error_patterns),
        "endpoint_stats": dict(endpoint_stats),
    }


def print_analysis(analysis):
    """Print formatted analysis"""
    print("\n" + "="*80)
    print("📊 CLOUD RUN LOG ANALYSIS")
    print("="*80)
    
    # Error summary
    print(f"\n🔴 ERRORS: {len(analysis['errors'])}")
    if analysis['errors']:
        print("\nRecent errors:")
        for error in analysis['errors'][:5]:  # Show last 5
            print(f"  [{error['timestamp']}]")
            print(f"  {error['message'][:200]}...")
            print()
    
    # Error patterns
    if analysis['error_patterns']:
        print("\n🔍 ERROR PATTERNS:")
        for pattern, count in sorted(analysis['error_patterns'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} occurrences")
    
    # Warnings
    print(f"\n⚠️  WARNINGS: {len(analysis['warnings'])}")
    if analysis['warnings']:
        print("\nRecent warnings:")
        for warning in analysis['warnings'][:3]:  # Show last 3
            print(f"  [{warning['timestamp']}]")
            print(f"  {warning['message'][:150]}...")
            print()
    
    # Endpoint stats
    print("\n📈 ENDPOINT STATISTICS:")
    for endpoint, stats in sorted(analysis['endpoint_stats'].items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
        error_rate = (stats['errors'] / stats['count'] * 100) if stats['count'] > 0 else 0
        status = "🔴" if error_rate > 50 else "⚠️ " if error_rate > 10 else "✅"
        print(f"  {status} {endpoint}: {stats['count']} requests, {stats['errors']} errors ({error_rate:.1f}%)")
    
    print("\n" + "="*80)


def main():
    """Main entry point"""
    print("🔍 Fetching Cloud Run logs...")
    logs = fetch_logs(limit=200)
    
    if not logs:
        print("❌ No logs found or error fetching logs")
        return
    
    print(f"✅ Fetched {len(logs)} log entries")
    
    analysis = analyze_logs(logs)
    print_analysis(analysis)
    
    # Save detailed analysis to file
    output_file = "cloud_logs_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\n💾 Detailed analysis saved to: {output_file}")


if __name__ == "__main__":
    main()

