"""
Example: Scan MT5 account for rule violations using Ollama
"""
import asyncio
import requests
from src.ollama_rule_scanner import scan_mt5_account, OllamaRuleScanner


def example_with_mock_data():
    """Example with mock account data (no MT5 API required)"""
    print("🔍 Running Ollama Rule Scanner Example (Mock Data)")
    print()
    
    # Mock account data (simulates MT5 API response)
    mock_account = {
        "balance": 100000.00,
        "equity": 95500.00,
        "profit": -4500.00,
        "margin": 2000.00,
        "margin_free": 93500.00,
        "margin_level": 4775.00,
        "positions": [
            {
                "ticket": 123456,
                "symbol": "EURUSD",
                "volume": 2.0,
                "type": 0,
                "price_open": 1.0850,
                "price_current": 1.0820,
                "profit": -600.00,
                "sl": 1.0800,
                "tp": 1.0900
            },
            {
                "ticket": 123457,
                "symbol": "GBPUSD",
                "volume": 1.5,
                "type": 1,
                "price_open": 1.2650,
                "price_current": 1.2680,
                "profit": -450.00,
                "sl": 1.2700,
                "tp": 1.2600
            }
        ]
    }
    
    # Initialize scanner
    scanner = OllamaRuleScanner(model="qwen2.5-coder:14b")
    
    # Scan for violations
    report = scanner.scan_account(mock_account, firm_name="FTMO")
    
    # Print report
    scanner.print_report(report)
    
    # Save report
    scanner.save_report(report, "example_rule_violation_report.json")
    
    return report


async def example_with_live_mt5():
    """Example with live MT5 API (requires running API server and valid token)"""
    print("🔍 Running Ollama Rule Scanner Example (Live MT5)")
    print()
    
    # Configuration
    MT5_API_URL = "http://localhost:8000"
    SESSION_TOKEN = None  # Set your session token here
    FIRM_NAME = "FTMO"
    
    if not SESSION_TOKEN:
        print("⚠️  No session token provided. Please:")
        print("1. Start MT5 API: python run_mt5_api.py")
        print("2. Login via web client or API")
        print("3. Set SESSION_TOKEN in this script")
        print()
        print("Using mock data instead...")
        return example_with_mock_data()
    
    # Scan live account
    report = await scan_mt5_account(
        api_url=MT5_API_URL,
        token=SESSION_TOKEN,
        firm_name=FIRM_NAME,
        ollama_model="llama3.2"
    )
    
    return report


def check_ollama_status():
    """Check if Ollama is running and what models are available"""
    print("🔍 Checking Ollama Status...")
    print()
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('models', [])
        
        print(f"✅ Ollama is running")
        print(f"📦 Available models: {len(models)}")
        print()
        
        if models:
            print("Models:")
            for model in models:
                name = model.get('name', 'unknown')
                size = model.get('size', 0) / (1024**3)  # Convert to GB
                print(f"  - {name} ({size:.2f} GB)")
        else:
            print("⚠️  No models found. Install a model:")
            print("  ollama pull llama3.2")
            print("  ollama pull mistral")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama not accessible: {e}")
        print()
        print("💡 Install and start Ollama:")
        print("  1. Download from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull llama3.2")
        print()
        return False


if __name__ == "__main__":
    print("=" * 80)
    print("Ollama Rule Violation Scanner - Example Usage")
    print("=" * 80)
    print()
    
    # Check Ollama
    if not check_ollama_status():
        print("⚠️  Ollama is required. Exiting...")
        exit(1)
    
    # Run example
    print("Choose example mode:")
    print("1. Mock data (no MT5 API required)")
    print("2. Live MT5 account (requires running API)")
    print()
    
    choice = input("Enter choice (1 or 2, default=1): ").strip() or "1"
    print()
    
    if choice == "2":
        asyncio.run(example_with_live_mt5())
    else:
        example_with_mock_data()
    
    print()
    print("✅ Example complete!")
    print()
    print("Next steps:")
    print("  - Review the generated report JSON")
    print("  - Customize rules in database")
    print("  - Integrate into your monitoring pipeline")
