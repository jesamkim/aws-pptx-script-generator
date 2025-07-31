#!/usr/bin/env python3
"""
AWS PowerPoint Script Generator - Environment Repair Script
Version: 2.1.0
Last Updated: July 31, 2025

This script automatically repairs common environment issues.
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
from validate_environment import EnvironmentValidator, ValidationResult, Colors

class EnvironmentRepairer:
    """Automatic environment repair tool."""
    
    def __init__(self, project_root: Optional[str] = None):
        """Initialize the repairer.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.validator = EnvironmentValidator(str(self.project_root))
        self.repair_log = self.project_root / "repair.log"
        
        # Initialize repair logging
        self._init_repair_logging()
    
    def _init_repair_logging(self):
        """Initialize repair logging."""
        with open(self.repair_log, 'w') as f:
            f.write("=== Environment Repair Log ===\n")
            f.write(f"Started at: {datetime.now()}\n")
            f.write("=" * 40 + "\n\n")
    
    def _log_repair(self, message: str):
        """Log repair action."""
        with open(self.repair_log, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
    
    def _print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message."""
        print(f"{color}{message}{Colors.NC}")
    
    def _run_command(self, command: List[str], capture_output: bool = True) -> tuple:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                timeout=300  # 5 minute timeout for repairs
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def repair_virtual_environment(self) -> bool:
        """Repair virtual environment issues."""
        self._print_colored("🔧 Repairing virtual environment...", Colors.YELLOW)
        self._log_repair("Attempting to repair virtual environment")
        
        venv_path = self.project_root / "aws-venv"
        
        # Remove existing broken environment
        if venv_path.exists():
            self._print_colored("   Removing existing virtual environment...", Colors.BLUE)
            shutil.rmtree(venv_path)
        
        # Create new virtual environment
        self._print_colored("   Creating new virtual environment...", Colors.BLUE)
        success, stdout, stderr = self._run_command([sys.executable, "-m", "venv", str(venv_path)])
        
        if not success:
            self._print_colored(f"   ❌ Failed to create virtual environment: {stderr}", Colors.RED)
            self._log_repair(f"Failed to create venv: {stderr}")
            return False
        
        self._print_colored("   ✅ Virtual environment created successfully", Colors.GREEN)
        self._log_repair("Virtual environment created successfully")
        return True
    
    def repair_required_packages(self) -> bool:
        """Repair missing Python packages."""
        self._print_colored("🔧 Repairing Python packages...", Colors.YELLOW)
        self._log_repair("Attempting to repair Python packages")
        
        # Upgrade pip first
        self._print_colored("   Upgrading pip...", Colors.BLUE)
        success, stdout, stderr = self._run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        if not success:
            self._print_colored(f"   ⚠️  Failed to upgrade pip: {stderr}", Colors.YELLOW)
        
        # Install requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self._print_colored("   Installing requirements.txt...", Colors.BLUE)
            success, stdout, stderr = self._run_command([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            
            if not success:
                self._print_colored(f"   ❌ Failed to install requirements: {stderr}", Colors.RED)
                self._log_repair(f"Failed to install requirements: {stderr}")
                return False
        
        # Install critical MCP packages
        critical_packages = [
            "awslabs-aws-documentation-mcp-server",
            "pydantic-settings",
            "python-mcp-client"
        ]
        
        for package in critical_packages:
            self._print_colored(f"   Installing {package}...", Colors.BLUE)
            success, stdout, stderr = self._run_command([
                sys.executable, "-m", "pip", "install", package
            ])
            
            if not success:
                self._print_colored(f"   ⚠️  Failed to install {package}: {stderr}", Colors.YELLOW)
                self._log_repair(f"Failed to install {package}: {stderr}")
        
        self._print_colored("   ✅ Package installation completed", Colors.GREEN)
        self._log_repair("Package installation completed")
        return True
    
    def repair_env_file(self) -> bool:
        """Repair .env file."""
        self._print_colored("🔧 Repairing .env file...", Colors.YELLOW)
        self._log_repair("Attempting to repair .env file")
        
        env_file = self.project_root / ".env"
        
        # Create default .env file
        env_content = """# AWS Configuration
AWS_DEFAULT_REGION=us-west-2
AWS_REGION=us-west-2
AWS_PROFILE=default

# Bedrock Configuration
BEDROCK_MODEL_ID=us.anthropic.claude-3-7-sonnet-20250219-v1:0

# Application Settings
LOG_LEVEL=INFO
CACHE_TTL=3600
MAX_WORKERS=4

# MCP Configuration
MCP_TIMEOUT=30
MCP_LOG_LEVEL=ERROR
"""
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            self._print_colored("   ✅ .env file created successfully", Colors.GREEN)
            self._log_repair(".env file created successfully")
            return True
            
        except Exception as e:
            self._print_colored(f"   ❌ Failed to create .env file: {e}", Colors.RED)
            self._log_repair(f"Failed to create .env file: {e}")
            return False
    
    def repair_mcp_configuration(self) -> bool:
        """Repair MCP configuration."""
        self._print_colored("🔧 Repairing MCP configuration...", Colors.YELLOW)
        self._log_repair("Attempting to repair MCP configuration")
        
        mcp_config_file = self.project_root / "mcp-settings.json"
        
        # Create default MCP configuration
        mcp_config = {
            "mcpServers": {
                "awslabs.aws-documentation-mcp-server": {
                    "command": "python",
                    "args": [
                        "-c", "from awslabs.aws_documentation_mcp_server.server import main; main()"
                    ],
                    "env": {
                        "FASTMCP_LOG_LEVEL": "ERROR",
                        "AWS_DOCUMENTATION_PARTITION": "aws"
                    },
                    "disabled": False,
                    "autoApprove": [
                        "search_documentation",
                        "read_documentation",
                        "recommend"
                    ]
                }
            }
        }
        
        try:
            with open(mcp_config_file, 'w') as f:
                json.dump(mcp_config, f, indent=2)
            
            self._print_colored("   ✅ MCP configuration created successfully", Colors.GREEN)
            self._log_repair("MCP configuration created successfully")
            return True
            
        except Exception as e:
            self._print_colored(f"   ❌ Failed to create MCP configuration: {e}", Colors.RED)
            self._log_repair(f"Failed to create MCP configuration: {e}")
            return False
    
    def repair_project_structure(self) -> bool:
        """Repair missing project directories."""
        self._print_colored("🔧 Repairing project structure...", Colors.YELLOW)
        self._log_repair("Attempting to repair project structure")
        
        required_dirs = [
            "src",
            "src/mcp_integration",
            "config",
            "tests",
            "logs",
            "scripts"
        ]
        
        created_dirs = []
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    created_dirs.append(dir_path)
                    self._print_colored(f"   Created directory: {dir_path}", Colors.BLUE)
                except Exception as e:
                    self._print_colored(f"   ❌ Failed to create {dir_path}: {e}", Colors.RED)
                    self._log_repair(f"Failed to create directory {dir_path}: {e}")
                    return False
        
        if created_dirs:
            self._print_colored(f"   ✅ Created {len(created_dirs)} directories", Colors.GREEN)
            self._log_repair(f"Created directories: {', '.join(created_dirs)}")
        else:
            self._print_colored("   ✅ All required directories exist", Colors.GREEN)
        
        return True
    
    def run_automatic_repairs(self, validation_results: List[ValidationResult]) -> Dict[str, bool]:
        """Run automatic repairs based on validation results.
        
        Args:
            validation_results: List of validation results
            
        Returns:
            Dictionary mapping repair names to success status
        """
        self._print_colored("🔧 Starting automatic environment repairs...", Colors.CYAN)
        print()
        
        repair_results = {}
        
        # Map validation failures to repair functions
        repair_mapping = {
            "Virtual Environment": self.repair_virtual_environment,
            "Required Packages": self.repair_required_packages,
            "Environment Variables": self.repair_env_file,
            "MCP Configuration": self.repair_mcp_configuration,
            "Project Structure": self.repair_project_structure
        }
        
        # Find failed validations that can be repaired
        failed_results = [r for r in validation_results if not r.passed and r.fix_available]
        
        if not failed_results:
            self._print_colored("✅ No repairs needed - all validations passed!", Colors.GREEN)
            return repair_results
        
        self._print_colored(f"Found {len(failed_results)} issues that can be automatically repaired:", Colors.YELLOW)
        for result in failed_results:
            self._print_colored(f"   • {result.name}: {result.message}", Colors.YELLOW)
        print()
        
        # Run repairs
        for result in failed_results:
            if result.name in repair_mapping:
                repair_func = repair_mapping[result.name]
                try:
                    success = repair_func()
                    repair_results[result.name] = success
                except Exception as e:
                    self._print_colored(f"❌ Repair failed for {result.name}: {e}", Colors.RED)
                    self._log_repair(f"Repair failed for {result.name}: {e}")
                    repair_results[result.name] = False
            else:
                self._print_colored(f"⚠️  No automatic repair available for: {result.name}", Colors.YELLOW)
                repair_results[result.name] = False
        
        return repair_results
    
    def print_repair_summary(self, repair_results: Dict[str, bool]):
        """Print repair summary."""
        successful_repairs = sum(1 for success in repair_results.values() if success)
        total_repairs = len(repair_results)
        
        print()
        self._print_colored("=" * 60, Colors.CYAN)
        self._print_colored("🔧 REPAIR SUMMARY", Colors.CYAN)
        self._print_colored("=" * 60, Colors.CYAN)
        
        if successful_repairs == total_repairs and total_repairs > 0:
            self._print_colored(f"🎉 All {total_repairs} repairs completed successfully!", Colors.GREEN)
        elif successful_repairs > 0:
            self._print_colored(f"✅ {successful_repairs} of {total_repairs} repairs completed successfully", Colors.YELLOW)
        else:
            self._print_colored("❌ No repairs were successful", Colors.RED)
        
        # Show individual repair results
        if repair_results:
            print()
            self._print_colored("Repair Details:", Colors.BLUE)
            for repair_name, success in repair_results.items():
                status = "✅ SUCCESS" if success else "❌ FAILED"
                color = Colors.GREEN if success else Colors.RED
                self._print_colored(f"   {repair_name}: {status}", color)
        
        print()
        self._print_colored("📄 Repair log saved to: repair.log", Colors.BLUE)
        
        if successful_repairs > 0:
            print()
            self._print_colored("🔄 Recommended next steps:", Colors.YELLOW)
            self._print_colored("   1. Run validation again: python scripts/validate_environment.py", Colors.BLUE)
            self._print_colored("   2. If all checks pass, start the application: ./start.sh", Colors.BLUE)
        
        print()

def main():
    """Main function to run environment repairs."""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="AWS PowerPoint Script Generator - Environment Repairer")
    parser.add_argument("--project-root", help="Path to project root directory")
    parser.add_argument("--validate-first", action="store_true", help="Run validation before repairs")
    
    args = parser.parse_args()
    
    # Initialize repairer
    repairer = EnvironmentRepairer(args.project_root)
    
    validation_results = []
    
    if args.validate_first:
        # Run validation first
        print("🔍 Running validation to identify issues...")
        validation_results = repairer.validator.run_all_validations()
        print()
    else:
        # Create dummy validation results for all possible repairs
        validation_results = [
            ValidationResult("Virtual Environment", False, "Needs repair", fix_available=True),
            ValidationResult("Required Packages", False, "Needs repair", fix_available=True),
            ValidationResult("Environment Variables", False, "Needs repair", fix_available=True),
            ValidationResult("MCP Configuration", False, "Needs repair", fix_available=True),
            ValidationResult("Project Structure", False, "Needs repair", fix_available=True)
        ]
    
    # Run repairs
    repair_results = repairer.run_automatic_repairs(validation_results)
    
    # Print summary
    repairer.print_repair_summary(repair_results)
    
    # Exit with appropriate code
    if repair_results and all(repair_results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
