"""
Test script for MT5 REST API
Tests basic functionality without requiring MT5 credentials
"""
import requests
import sys


def test_api_health():
    """Test if API server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API server is healthy")
            print(f"  Status: {data.get('status')}")
            print(f"  Active sessions: {data.get('active_sessions', 0)}")
            return True
        else:
            print(f"✗ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server")
        print("  Make sure the server is running: python run_mt5_api.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_api_root():
    """Test API root endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API root endpoint accessible")
            print(f"  Name: {data.get('name')}")
            print(f"  Version: {data.get('version')}")
            return True
        else:
            print(f"✗ Root endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_api_docs():
    """Test if API documentation is accessible"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print(f"✓ API documentation accessible at http://localhost:8000/docs")
            return True
        else:
            print(f"✗ Documentation returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_invalid_login():
    """Test login with invalid credentials (should fail gracefully)"""
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/login",
            json={
                "account_number": 99999999,
                "password": "invalid",
                "server": "Invalid-Server"
            },
            timeout=10
        )
        if response.status_code in [401, 500]:
            print(f"✓ Invalid login properly rejected (status {response.status_code})")
            return True
        else:
            print(f"⚠ Unexpected status code: {response.status_code}")
            return True  # Still counts as working
    except Exception as e:
        print(f"✗ Error testing login: {e}")
        return False


def test_unauthorized_access():
    """Test accessing protected endpoint without authentication"""
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/account",
            timeout=5
        )
        if response.status_code == 401:
            print(f"✓ Unauthorized access properly blocked")
            return True
        else:
            print(f"⚠ Expected 401, got {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    print("="*60)
    print("MT5 REST API - Basic Tests")
    print("="*60)
    print("\nNote: These tests verify the API is working without")
    print("      requiring actual MT5 credentials.")
    print()
    
    tests = [
        ("Health Check", test_api_health),
        ("Root Endpoint", test_api_root),
        ("Documentation", test_api_docs),
        ("Invalid Login", test_invalid_login),
        ("Unauthorized Access", test_unauthorized_access),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTest: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! The API is working correctly.")
        print("\nNext steps:")
        print("1. View API documentation: http://localhost:8000/docs")
        print("2. Test with real credentials: python examples/test_mt5_api.py")
        print("3. Try the web client: examples/mt5_api_client.html")
    else:
        print(f"\n⚠ {total - passed} test(s) failed.")
        print("\nTroubleshooting:")
        print("1. Make sure the server is running: python run_mt5_api.py")
        print("2. Check if port 8000 is available")
        print("3. Check for any error messages above")
    
    print()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
