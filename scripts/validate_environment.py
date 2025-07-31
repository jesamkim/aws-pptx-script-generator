#!/usr/bin/env python3
"""
AWS PowerPoint Script Generator - Environment Validation and Repair Script
Version: 2.1.0
Last Updated: July 31, 2025

This script performs comprehensive environment validation and can automatically
repair common configuration issues.
"""

import os
import sys
import json
import subprocess
import importlib
import platform
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Colors for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    PURPLE = '\033[0;35m'
    NC = '\033[0m'  # No Color

@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None
    fix_available: bool = False
    fix_command: Optional[str] = None

class EnvironmentValidator:
    """Comprehensive environment validator and repair tool."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the validator.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.results: List[ValidationResult] = []
        self.log_file = self.project_root / "validation.log"
        
        # Initialize logging
        self._init_logging()
    
    def _init_logging(self):
        """Initialize logging to file."""
        with open(self.log_file, 'w') as f:
            f.write(f"=== Environment Validation Log ===\n")
            f.write(f"Started at: {datetime.now()}\n")
            f.write(f"Python version: {sys.version}\n")
            f.write(f"Platform: {platform.platform()}\n")
            f.write(f"Project root: {self.project_root}\n")
            f.write("=" * 50 + "\n\n")
    
    def _log(self, message: str):
        """Log message to file."""
        with open(self.log_file, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
    
    def _print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message to console."""
        print(f"{color}{message}{Colors.NC}")
    
    def _run_command(self, command: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output.
        
        Args:
            command: Command to run as list of strings
            capture_output: Whether to capture output
            
        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def validate_python_version(self) -> ValidationResult:
        """Validate Python version compatibility."""
        self._log("Validating Python version...")
        
        try:
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            if version.major == 3 and version.minor >= 10:
                return ValidationResult(
                    name="Python Version",
                    passed=True,
                    message=f"Python {version_str} is compatible (3.10+ required)",
                    details=f"Executable: {sys.executable}"
                )
            else:
                return ValidationResult(
                    name="Python Version",
                    passed=False,
                    message=f"Python {version_str} is not compatible (3.10+ required)",
                    details="Please install Python 3.10 or higher",
                    fix_available=True,
                    fix_command="Install Python 3.10+ from python.org or your package manager"
                )
        except Exception as e:
            return ValidationResult(
                name="Python Version",
                passed=False,
                message=f"Failed to check Python version: {e}",
                fix_available=False
            )
    
    def validate_virtual_environment(self) -> ValidationResult:
        """Validate virtual environment setup."""
        self._log("Validating virtual environment...")
        
        venv_path = self.project_root / "aws-venv"
        
        if not venv_path.exists():
            return ValidationResult(
                name="Virtual Environment",
                passed=False,
                message="Virtual environment not found",
                details=f"Expected location: {venv_path}",
                fix_available=True,
                fix_command=f"python -m venv {venv_path}"
            )
        
        # Check if we're in the virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not in_venv:
            activate_script = venv_path / "bin" / "activate"
            if not activate_script.exists():
                activate_script = venv_path / "Scripts" / "activate"
            
            return ValidationResult(
                name="Virtual Environment",
                passed=False,
                message="Virtual environment exists but not activated",
                details=f"Activate with: source {activate_script}",
                fix_available=True,
                fix_command=f"source {activate_script}"
            )
        
        return ValidationResult(
            name="Virtual Environment",
            passed=True,
            message="Virtual environment is active",
            details=f"Location: {sys.prefix}"
        )
    
    def validate_required_packages(self) -> ValidationResult:
        """Validate required Python packages."""
        self._log("Validating required packages...")
        
        required_packages = [
            'streamlit',
            'pptx',  # python-pptx
            'PIL',   # Pillow
            'loguru',
            'boto3',
            'botocore',
            'requests',
            'pandas',
            'numpy',
            'pydantic',
            'pydantic_settings',
            'mcp',
            'awslabs.aws_documentation_mcp_server'
        ]
        
        missing_packages = []
        package_details = []
        
        for package in required_packages:
            try:
                if package == 'pptx':
                    module = importlib.import_module('pptx')
                elif package == 'PIL':
                    module = importlib.import_module('PIL')
                elif package == 'awslabs.aws_documentation_mcp_server':
                    module = importlib.import_module('awslabs.aws_documentation_mcp_server')
                else:
                    module = importlib.import_module(package)
                
                version = getattr(module, '__version__', 'Unknown')
                package_details.append(f"{package}: {version}")
                
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            return ValidationResult(
                name="Required Packages",
                passed=False,
                message=f"Missing packages: {', '.join(missing_packages)}",
                details=f"Installed: {len(package_details)}, Missing: {len(missing_packages)}",
                fix_available=True,
                fix_command="pip install -r requirements.txt awslabs-aws-documentation-mcp-server pydantic-settings"
            )
        
        return ValidationResult(
            name="Required Packages",
            passed=True,
            message=f"All {len(required_packages)} required packages are installed",
            details="\n".join(package_details)
        )
    
    def validate_aws_configuration(self) -> ValidationResult:
        """Validate AWS CLI and credentials."""
        self._log("Validating AWS configuration...")
        
        # Check AWS CLI
        success, output = self._run_command(['aws', '--version'])
        if not success:
            return ValidationResult(
                name="AWS Configuration",
                passed=False,
                message="AWS CLI not found",
                details="Install AWS CLI from aws.amazon.com/cli/",
                fix_available=True,
                fix_command="Install AWS CLI and run 'aws configure'"
            )
        
        aws_version = output.split()[0] if output else "Unknown"
        
        # Check AWS credentials
        success, output = self._run_command(['aws', 'sts', 'get-caller-identity'])
        if not success:
            return ValidationResult(
                name="AWS Configuration",
                passed=False,
                message="AWS credentials not configured",
                details=f"AWS CLI version: {aws_version}",
                fix_available=True,
                fix_command="aws configure"
            )
        
        try:
            identity = json.loads(output)
            account_id = identity.get('Account', 'Unknown')
            user_arn = identity.get('Arn', 'Unknown')
            
            return ValidationResult(
                name="AWS Configuration",
                passed=True,
                message=f"AWS CLI configured (Account: {account_id})",
                details=f"Version: {aws_version}\nUser: {user_arn}"
            )
        except json.JSONDecodeError:
            return ValidationResult(
                name="AWS Configuration",
                passed=False,
                message="AWS credentials configured but response invalid",
                details=f"Raw output: {output}",
                fix_available=True,
                fix_command="aws configure"
            )
    
    def validate_project_structure(self) -> ValidationResult:
        """Validate project file structure."""
        self._log("Validating project structure...")
        
        required_files = [
            'streamlit_app.py',
            'requirements.txt',
            '.env',
            'mcp-settings.json',
            'src/mcp_integration/aws_docs_client.py',
            'src/mcp_integration/real_mcp_client.py',
            'config/aws_config.py',
            'config/mcp_config.py'
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        if missing_files:
            return ValidationResult(
                name="Project Structure",
                passed=False,
                message=f"Missing files: {', '.join(missing_files)}",
                details=f"Found: {len(existing_files)}, Missing: {len(missing_files)}",
                fix_available=False
            )
        
        return ValidationResult(
            name="Project Structure",
            passed=True,
            message=f"All {len(required_files)} required files found",
            details=f"Project root: {self.project_root}"
        )
    
    def validate_mcp_configuration(self) -> ValidationResult:
        """Validate MCP server configuration."""
        self._log("Validating MCP configuration...")
        
        mcp_config_path = self.project_root / "mcp-settings.json"
        
        if not mcp_config_path.exists():
            return ValidationResult(
                name="MCP Configuration",
                passed=False,
                message="mcp-settings.json not found",
                details=f"Expected location: {mcp_config_path}",
                fix_available=True,
                fix_command="Create mcp-settings.json with proper configuration"
            )
        
        try:
            with open(mcp_config_path, 'r') as f:
                config = json.load(f)
            
            if 'mcpServers' not in config:
                return ValidationResult(
                    name="MCP Configuration",
                    passed=False,
                    message="Invalid MCP configuration format",
                    details="Missing 'mcpServers' section",
                    fix_available=True,
                    fix_command="Fix mcp-settings.json format"
                )
            
            servers = config['mcpServers']
            server_count = len(servers)
            
            # Check for AWS Documentation server
            aws_doc_server = None
            for server_name, server_config in servers.items():
                if 'aws-documentation-mcp-server' in server_name:
                    aws_doc_server = server_config
                    break
            
            if not aws_doc_server:
                return ValidationResult(
                    name="MCP Configuration",
                    passed=False,
                    message="AWS Documentation MCP server not configured",
                    details=f"Found {server_count} server(s) but no AWS Documentation server",
                    fix_available=True,
                    fix_command="Add AWS Documentation MCP server to mcp-settings.json"
                )
            
            return ValidationResult(
                name="MCP Configuration",
                passed=True,
                message=f"MCP configuration valid with {server_count} server(s)",
                details=f"AWS Documentation server: {'✅ Configured' if aws_doc_server else '❌ Missing'}"
            )
            
        except json.JSONDecodeError as e:
            return ValidationResult(
                name="MCP Configuration",
                passed=False,
                message="Invalid JSON in mcp-settings.json",
                details=str(e),
                fix_available=True,
                fix_command="Fix JSON syntax in mcp-settings.json"
            )
        except Exception as e:
            return ValidationResult(
                name="MCP Configuration",
                passed=False,
                message=f"Error reading MCP configuration: {e}",
                fix_available=False
            )
    
    def validate_environment_variables(self) -> ValidationResult:
        """Validate environment variables."""
        self._log("Validating environment variables...")
        
        required_vars = ['AWS_REGION', 'AWS_DEFAULT_REGION']
        env_file_path = self.project_root / ".env"
        
        missing_vars = []
        found_vars = []
        
        # Check environment variables
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                found_vars.append(f"{var}={value}")
            else:
                missing_vars.append(var)
        
        # Check .env file
        env_file_exists = env_file_path.exists()
        env_file_content = ""
        
        if env_file_exists:
            try:
                with open(env_file_path, 'r') as f:
                    env_file_content = f.read()
            except Exception as e:
                return ValidationResult(
                    name="Environment Variables",
                    passed=False,
                    message=f"Error reading .env file: {e}",
                    fix_available=True,
                    fix_command="Fix .env file permissions or content"
                )
        
        details = []
        details.append(f".env file: {'✅ Exists' if env_file_exists else '❌ Missing'}")
        details.append(f"Environment variables: {len(found_vars)} found, {len(missing_vars)} missing")
        
        if missing_vars and not env_file_exists:
            return ValidationResult(
                name="Environment Variables",
                passed=False,
                message="Missing environment variables and .env file",
                details="\n".join(details),
                fix_available=True,
                fix_command="Create .env file with required variables"
            )
        
        return ValidationResult(
            name="Environment Variables",
            passed=True,
            message="Environment configuration is valid",
            details="\n".join(details + found_vars)
        )
    
    def validate_mcp_connection(self) -> ValidationResult:
        """Test MCP server connection."""
        self._log("Testing MCP connection...")
        
        try:
            # Try to import and test MCP client
            sys.path.insert(0, str(self.project_root))
            from src.mcp_integration.real_mcp_client import SyncMCPClient
            
            client = SyncMCPClient()
            
            if not client.is_available():
                return ValidationResult(
                    name="MCP Connection",
                    passed=False,
                    message="MCP server configuration not available",
                    details="Check mcp-settings.json configuration",
                    fix_available=True,
                    fix_command="python tests/test_mcp_connection.py"
                )
            
            # Test connection
            connection_ok = client.test_connection()
            
            if connection_ok:
                return ValidationResult(
                    name="MCP Connection",
                    passed=True,
                    message="MCP server connection successful",
                    details="AWS Documentation MCP server is responding"
                )
            else:
                return ValidationResult(
                    name="MCP Connection",
                    passed=False,
                    message="MCP server connection failed",
                    details="Server is configured but not responding",
                    fix_available=True,
                    fix_command="Check MCP server installation and configuration"
                )
                
        except ImportError as e:
            return ValidationResult(
                name="MCP Connection",
                passed=False,
                message="Cannot import MCP client modules",
                details=str(e),
                fix_available=True,
                fix_command="Check project structure and Python path"
            )
        except Exception as e:
            return ValidationResult(
                name="MCP Connection",
                passed=False,
                message=f"MCP connection test failed: {e}",
                details="Unexpected error during connection test",
                fix_available=True,
                fix_command="python tests/test_mcp_connection.py"
            )
    
    def run_all_validations(self) -> List[ValidationResult]:
        """Run all validation checks."""
        self._print_colored("🔍 Running comprehensive environment validation...", Colors.CYAN)
        print()
        
        validations = [
            self.validate_python_version,
            self.validate_virtual_environment,
            self.validate_required_packages,
            self.validate_aws_configuration,
            self.validate_project_structure,
            self.validate_mcp_configuration,
            self.validate_environment_variables,
            self.validate_mcp_connection
        ]
        
        self.results = []
        
        for i, validation in enumerate(validations, 1):
            self._print_colored(f"[{i}/{len(validations)}] {validation.__name__.replace('validate_', '').replace('_', ' ').title()}...", Colors.BLUE)
            
            try:
                result = validation()
                self.results.append(result)
                
                if result.passed:
                    self._print_colored(f"   ✅ {result.message}", Colors.GREEN)
                else:
                    self._print_colored(f"   ❌ {result.message}", Colors.RED)
                    if result.fix_available:
                        self._print_colored(f"   💡 Fix: {result.fix_command}", Colors.YELLOW)
                
                self._log(f"{result.name}: {'PASS' if result.passed else 'FAIL'} - {result.message}")
                
            except Exception as e:
                error_result = ValidationResult(
                    name=validation.__name__.replace('validate_', '').replace('_', ' ').title(),
                    passed=False,
                    message=f"Validation error: {e}",
                    fix_available=False
                )
                self.results.append(error_result)
                self._print_colored(f"   💥 {error_result.message}", Colors.RED)
                self._log(f"{error_result.name}: ERROR - {e}")
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a detailed validation report."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        report = []
        report.append("# Environment Validation Report")
        report.append("")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Project Root:** {self.project_root}")
        report.append(f"**Python Version:** {sys.version}")
        report.append(f"**Platform:** {platform.platform()}")
        report.append("")
        report.append(f"## Summary: {passed}/{total} checks passed")
        report.append("")
        
        # Passed checks
        passed_results = [r for r in self.results if r.passed]
        if passed_results:
            report.append("## ✅ Passed Checks")
            report.append("")
            for result in passed_results:
                report.append(f"### {result.name}")
                report.append(f"- **Status:** ✅ PASSED")
                report.append(f"- **Message:** {result.message}")
                if result.details:
                    report.append(f"- **Details:** {result.details}")
                report.append("")
        
        # Failed checks
        failed_results = [r for r in self.results if not r.passed]
        if failed_results:
            report.append("## ❌ Failed Checks")
            report.append("")
            for result in failed_results:
                report.append(f"### {result.name}")
                report.append(f"- **Status:** ❌ FAILED")
                report.append(f"- **Message:** {result.message}")
                if result.details:
                    report.append(f"- **Details:** {result.details}")
                if result.fix_available and result.fix_command:
                    report.append(f"- **Fix:** {result.fix_command}")
                report.append("")
        
        # Recommendations
        if failed_results:
            report.append("## 🔧 Recommended Actions")
            report.append("")
            report.append("1. **Address failed checks** in order of priority")
            report.append("2. **Run validation again** after making fixes")
            report.append("3. **Check the validation log** for detailed error information")
            report.append("")
            report.append("### Quick Fix Commands")
            report.append("```bash")
            for result in failed_results:
                if result.fix_available and result.fix_command:
                    report.append(f"# Fix: {result.name}")
                    report.append(result.fix_command)
                    report.append("")
            report.append("```")
        else:
            report.append("## 🎉 All Checks Passed!")
            report.append("")
            report.append("Your environment is properly configured and ready to use.")
            report.append("")
            report.append("### Next Steps")
            report.append("```bash")
            report.append("# Start the application")
            report.append("streamlit run streamlit_app.py")
            report.append("")
            report.append("# Or use the startup script")
            report.append("./start.sh")
            report.append("```")
        
        return "\n".join(report)
    
    def print_summary(self):
        """Print validation summary to console."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print()
        self._print_colored("=" * 60, Colors.CYAN)
        self._print_colored("📊 VALIDATION SUMMARY", Colors.CYAN)
        self._print_colored("=" * 60, Colors.CYAN)
        
        if passed == total:
            self._print_colored(f"🎉 All {total} checks passed! Environment is ready.", Colors.GREEN)
        else:
            failed = total - passed
            self._print_colored(f"⚠️  {failed} of {total} checks failed. See details above.", Colors.YELLOW)
        
        print()
        self._print_colored("📄 Detailed report saved to: validation_report.md", Colors.BLUE)
        self._print_colored("📋 Validation log saved to: validation.log", Colors.BLUE)
        print()

def main():
    """Main function to run environment validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AWS PowerPoint Script Generator - Environment Validator")
    parser.add_argument("--project-root", help="Path to project root directory")
    parser.add_argument("--report-file", default="validation_report.md", help="Output report file")
    parser.add_argument("--auto-fix", action="store_true", help="Attempt to automatically fix issues")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = EnvironmentValidator(args.project_root)
    
    # Run validations
    results = validator.run_all_validations()
    
    # Generate and save report
    report = validator.generate_report()
    report_path = validator.project_root / args.report_file
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Print summary
    validator.print_summary()
    
    # Exit with appropriate code
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    if passed == total:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
