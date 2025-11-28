"""
Quick setup script for MT5 REST API
Checks dependencies and provides setup guidance
"""
import sys
import subprocess
import importlib.util


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✓ Python version {version.major}.{version.minor}.{version.micro}")
    return True


def check_package(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    if spec is None:
        return False
    return True


def main():
    print("="*60)
    print("MT5 REST API - Setup Checker")
    print("="*60)
    print()
    
    # Check Python version
    print("1. Checking Python version...")
    if not check_python_version():
        sys.exit(1)
    print()
    
    # Check required packages
    print("2. Checking required packages...")
    packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "MetaTrader5": "MetaTrader5",
        "requests": "requests"
    }
    
    missing_packages = []
    for package, import_name in packages.items():
        if check_package(package, import_name):
            print(f"  ✓ {package}")
        else:
            print(f"  ❌ {package} (missing)")
            missing_packages.append(package)
    print()
    
    # Install missing packages
    if missing_packages:
        print("3. Installing missing packages...")
        print(f"   Missing: {', '.join(missing_packages)}")
        print()
        
        response = input("Would you like to install them now? (y/n): ")
        if response.lower() == 'y':
            print("\nInstalling packages...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
                ])
                print("\n✓ All packages installed successfully!")
            except subprocess.CalledProcessError:
                print("\n❌ Installation failed. Please run manually:")
                print("   pip install -r requirements.txt")
                sys.exit(1)
        else:
            print("\nPlease install missing packages manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    else:
        print("✓ All required packages are installed!")
    print()
    
    # Check MT5 availability
    print("3. Checking MetaTrader 5 availability...")
    try:
        import MetaTrader5 as mt5
        if mt5.initialize():
            version = mt5.version()
            print(f"  ✓ MT5 terminal found (version {version})")
            mt5.shutdown()
        else:
            print("  ⚠ MT5 terminal not accessible")
            print("    Make sure MT5 is installed and not running")
    except Exception as e:
        print(f"  ❌ MT5 check failed: {e}")
    print()
    
    # Final instructions
    print("="*60)
    print("Setup Complete! 🎉")
    print("="*60)
    print()
    print("Next steps:")
    print()
    print("1. Start the API server:")
    print("   python run_mt5_api.py")
    print()
    print("2. Access the API documentation:")
    print("   http://localhost:8000/docs")
    print()
    print("3. Try the web client:")
    print("   Open examples/mt5_api_client.html in your browser")
    print()
    print("4. Or use the Python client:")
    print("   python examples/test_mt5_api.py")
    print()
    print("5. Read the documentation:")
    print("   docs/MT5_API_QUICKSTART.md")
    print("   docs/MT5_REST_API.md")
    print()
    print("="*60)


if __name__ == "__main__":
    main()
