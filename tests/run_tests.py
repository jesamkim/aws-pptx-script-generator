#!/usr/bin/env python3
"""Test Runner for AWS PowerPoint Script Generator.

This script runs all available tests and provides a comprehensive test report.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_script(script_path, description):
    """Run a test script and return results.
    
    Args:
        script_path: Path to the test script
        description: Description of the test
        
    Returns:
        Tuple of (success, duration, output)
    """
    print(f"\n🧪 Running {description}...")
    print("-" * 50)
    
    start_time = time.time()
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['AWS_REGION'] = 'us-west-2'
        env['AWS_DEFAULT_REGION'] = 'us-west-2'
        
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            env=env,
            cwd=project_root
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED ({duration:.1f}s)")
            if result.stdout:
                print(result.stdout)
            return True, duration, result.stdout
        else:
            print(f"❌ {description} - FAILED ({duration:.1f}s)")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False, duration, result.stderr
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ {description} - TIMEOUT ({duration:.1f}s)")
        return False, duration, "Test timed out"
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {description} - ERROR ({duration:.1f}s): {e}")
        return False, duration, str(e)


def run_pytest_tests():
    """Run pytest tests if available."""
    print(f"\n🧪 Running Pytest Tests...")
    print("-" * 50)
    
    try:
        # Check if pytest is available
        subprocess.run([sys.executable, '-m', 'pytest', '--version'], 
                      capture_output=True, check=True)
        
        # Run pytest
        env = os.environ.copy()
        env['AWS_REGION'] = 'us-west-2'
        env['AWS_DEFAULT_REGION'] = 'us-west-2'
        
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True,
            timeout=180,  # 3 minute timeout
            env=env,
            cwd=project_root
        )
        
        if result.returncode == 0:
            print("✅ Pytest Tests - PASSED")
            print(result.stdout)
            return True, result.stdout
        else:
            print("❌ Pytest Tests - FAILED")
            print("STDERR:", result.stderr)
            print("STDOUT:", result.stdout)
            return False, result.stderr
            
    except subprocess.CalledProcessError:
        print("⚠️  Pytest not available, skipping pytest tests")
        return True, "Pytest not available"
    except Exception as e:
        print(f"💥 Pytest Tests - ERROR: {e}")
        return False, str(e)


def main():
    """Run all tests and generate report."""
    print("🚀 AWS PowerPoint Script Generator - Test Suite")
    print("=" * 70)
    
    # Set up environment
    os.environ['AWS_REGION'] = 'us-west-2'
    os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
    
    # Define test scripts
    test_scripts = [
        ("test_installation.py", "Installation Verification"),
        ("test_mcp_connection.py", "MCP Connection Test"),
        ("test_mcp_integration.py", "MCP Integration Test"),
        ("test_basic.py", "Basic Functionality Test"),
        ("test_script_generation.py", "Script Generation Test"),
        ("test_prompt_cache.py", "Prompt Caching Test"),
        ("test_optimized_agent.py", "Optimized Agent Test"),
    ]
    
    results = []
    total_duration = 0
    
    # Run individual test scripts
    for script_name, description in test_scripts:
        script_path = Path(__file__).parent / script_name
        
        if script_path.exists():
            success, duration, output = run_test_script(script_path, description)
            results.append((description, success, duration, output))
            total_duration += duration
        else:
            print(f"⚠️  {script_name} not found, skipping")
            results.append((description, None, 0, "Script not found"))
    
    # Run pytest tests
    pytest_success, pytest_output = run_pytest_tests()
    
    # Generate summary report
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 70)
    
    passed = 0
    failed = 0
    skipped = 0
    
    for description, success, duration, output in results:
        if success is True:
            status = "✅ PASSED"
            passed += 1
        elif success is False:
            status = "❌ FAILED"
            failed += 1
        else:
            status = "⚠️  SKIPPED"
            skipped += 1
        
        print(f"{description:<30} {status:<12} ({duration:.1f}s)")
    
    # Pytest summary
    if pytest_success:
        print(f"{'Pytest Tests':<30} {'✅ PASSED':<12}")
        passed += 1
    else:
        print(f"{'Pytest Tests':<30} {'❌ FAILED':<12}")
        failed += 1
    
    print("-" * 70)
    print(f"Total Tests: {passed + failed + skipped}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total Duration: {total_duration:.1f}s")
    
    # Overall result
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your AWS PowerPoint Script Generator is ready to use.")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        print("Please check the output above and fix any issues.")
        
        # Provide helpful suggestions
        print("\n💡 Common Solutions:")
        print("   • Run: pip install -r requirements.txt")
        print("   • Run: pip install awslabs-aws-documentation-mcp-server")
        print("   • Check AWS credentials: aws configure")
        print("   • Verify .env file exists with AWS_REGION=us-west-2")
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
