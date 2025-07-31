"""Installation Verification Test.

This script verifies that all required components are properly installed
and configured for the AWS PowerPoint Script Generator.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_python_version():
    """Check Python version compatibility."""
    print("🐍 Checking Python Version...")
    
    version = sys.version_info
    print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 10:
        print("   ✅ Python version is compatible (3.10+)")
        return True
    else:
        print("   ❌ Python 3.10+ required for MCP server compatibility")
        return False


def check_required_packages():
    """Check if all required packages are installed."""
    print("\n📦 Checking Required Packages...")
    
    required_packages = [
        'streamlit',
        'python_pptx',
        'PIL',  # Pillow
        'loguru',
        'boto3',
        'botocore',
        'requests',
        'pandas',
        'numpy',
        'pydantic',
        'pydantic_settings',
        'mcp',
        'python_mcp_client',
        'awslabs.aws_documentation_mcp_server'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                importlib.import_module('PIL')
            elif package == 'python_pptx':
                importlib.import_module('pptx')
            elif package == 'awslabs.aws_documentation_mcp_server':
                importlib.import_module('awslabs.aws_documentation_mcp_server')
            elif package == 'python_mcp_client':
                # This package exists but may not have a direct import
                # Check if it's installed via pip
                import subprocess
                result = subprocess.run(['pip', 'show', 'python-mcp-client'], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    raise ImportError("python-mcp-client not installed")
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NOT INSTALLED")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n   💡 Install missing packages:")
        if 'awslabs.aws_documentation_mcp_server' in missing_packages:
            print("      pip install awslabs-aws-documentation-mcp-server")
        if 'pydantic_settings' in missing_packages:
            print("      pip install pydantic-settings")
        if 'python_mcp_client' in missing_packages:
            print("      pip install python-mcp-client")
        print("      pip install -r requirements.txt")
        return False
    
    print("   🎉 All required packages are installed!")
    return True


def check_aws_configuration():
    """Check AWS configuration."""
    print("\n☁️  Checking AWS Configuration...")
    
    # Check AWS CLI
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ AWS CLI installed: {result.stdout.strip()}")
        else:
            print("   ⚠️  AWS CLI not found")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("   ⚠️  AWS CLI not found or not responding")
    
    # Check AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        
        if credentials:
            print("   ✅ AWS credentials configured")
            
            # Check region
            region = session.region_name or os.environ.get('AWS_DEFAULT_REGION')
            if region:
                print(f"   ✅ AWS region: {region}")
            else:
                print("   ⚠️  AWS region not set")
                return False
        else:
            print("   ❌ AWS credentials not configured")
            print("   💡 Run: aws configure")
            return False
            
    except Exception as e:
        print(f"   ❌ AWS configuration error: {e}")
        return False
    
    # Check Bedrock access
    try:
        import boto3
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        # This will fail if no permissions, but that's expected
        print("   ✅ Bedrock client can be created")
    except Exception as e:
        print(f"   ⚠️  Bedrock client issue: {e}")
    
    return True


def check_project_structure():
    """Check project file structure."""
    print("\n📁 Checking Project Structure...")
    
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
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n   💡 Missing files need to be created or restored")
        return False
    
    return True


def check_mcp_configuration():
    """Check MCP server configuration."""
    print("\n🔗 Checking MCP Configuration...")
    
    # Check mcp-settings.json
    mcp_config_path = project_root / 'mcp-settings.json'
    if not mcp_config_path.exists():
        print("   ❌ mcp-settings.json not found")
        return False
    
    try:
        import json
        with open(mcp_config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config:
            servers = config['mcpServers']
            print(f"   ✅ MCP configuration found with {len(servers)} server(s)")
            
            for server_name, server_config in servers.items():
                print(f"   📋 Server: {server_name}")
                print(f"      Command: {server_config.get('command', 'Not specified')}")
                print(f"      Disabled: {server_config.get('disabled', False)}")
        else:
            print("   ❌ Invalid MCP configuration format")
            return False
            
    except Exception as e:
        print(f"   ❌ Error reading MCP configuration: {e}")
        return False
    
    return True


def check_environment_variables():
    """Check required environment variables."""
    print("\n🌍 Checking Environment Variables...")
    
    required_env_vars = [
        'AWS_REGION',
        'AWS_DEFAULT_REGION'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ✅ {var}={value}")
        else:
            print(f"   ⚠️  {var} not set")
            missing_vars.append(var)
    
    # Check .env file
    env_file = project_root / '.env'
    if env_file.exists():
        print("   ✅ .env file exists")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if 'AWS_REGION' in content:
                    print("   ✅ .env contains AWS configuration")
                else:
                    print("   ⚠️  .env missing AWS configuration")
        except Exception as e:
            print(f"   ⚠️  Error reading .env file: {e}")
    else:
        print("   ⚠️  .env file not found")
    
    return len(missing_vars) == 0


def test_basic_imports():
    """Test basic project imports."""
    print("\n🔧 Testing Project Imports...")
    
    try:
        from src.mcp_integration.aws_docs_client import AWSDocsClient
        print("   ✅ AWSDocsClient import successful")
        
        from src.mcp_integration.real_mcp_client import SyncMCPClient
        print("   ✅ SyncMCPClient import successful")
        
        from config.aws_config import aws_config
        print("   ✅ AWS config import successful")
        
        from config.mcp_config import mcp_client
        print("   ✅ MCP config import successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_installation_verification():
    """Run complete installation verification."""
    print("🔍 AWS PowerPoint Script Generator - Installation Verification")
    print("=" * 70)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_required_packages),
        ("AWS Configuration", check_aws_configuration),
        ("Project Structure", check_project_structure),
        ("MCP Configuration", check_mcp_configuration),
        ("Environment Variables", check_environment_variables),
        ("Project Imports", test_basic_imports)
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print(f"   ❌ {check_name} check failed with error: {e}")
            results[check_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Installation Verification Summary:")
    print("=" * 70)
    
    passed = 0
    total = len(checks)
    
    for check_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {check_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Installation verification completed successfully!")
        print("   Your environment is ready to run the AWS PowerPoint Script Generator.")
        return True
    else:
        print(f"\n⚠️  {total - passed} checks failed. Please address the issues above.")
        print("   Refer to the installation guide for detailed setup instructions.")
        return False


if __name__ == "__main__":
    success = run_installation_verification()
    sys.exit(0 if success else 1)
