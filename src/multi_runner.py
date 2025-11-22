"""
Multi-account runner for monitoring multiple trading accounts simultaneously
"""
import asyncio
import sys
from pathlib import Path
from src.config import AccountManager
from src.runner import RiskMonitor


class MultiAccountMonitor:
    """Monitor multiple trading accounts simultaneously"""
    
    def __init__(self, config_file: str = "accounts.json"):
        """
        Initialize multi-account monitor
        
        Args:
            config_file: Path to accounts configuration JSON file
        """
        self.config_file = config_file
        self.account_manager = AccountManager(config_file)
        self.monitors = []
        self.running = False
    
    async def monitor_account(self, monitor: RiskMonitor):
        """Run a single account monitor in async loop"""
        while self.running:
            try:
                monitor.check_once()
            except Exception as e:
                print(f"Error monitoring {monitor.account_config.label}: {e}")
            
            await asyncio.sleep(monitor.account_config.check_interval)
    
    async def start_async(self):
        """Start monitoring all enabled accounts asynchronously"""
        self.running = True
        
        enabled_accounts = self.account_manager.get_enabled_accounts()
        
        if not enabled_accounts:
            print("No enabled accounts found in configuration!")
            return
        
        print(f"\n{'='*60}")
        print(f"Starting Multi-Account Risk Monitor")
        print(f"{'='*60}")
        print(f"Monitoring {len(enabled_accounts)} account(s):\n")
        
        # Create monitors for each enabled account
        for account in enabled_accounts:
            try:
                monitor = RiskMonitor(account_config=account)
                self.monitors.append(monitor)
                
                print(f"✓ {account.label}")
                print(f"  Firm: {account.firm} ({account.rules.name})")
                print(f"  Platform: {account.platform.upper()}")
                print(f"  Starting Balance: ${account.starting_balance:,.2f}")
                print(f"  Check Interval: {account.check_interval}s")
                print()
                
            except Exception as e:
                print(f"✗ Failed to initialize {account.label}: {e}\n")
        
        if not self.monitors:
            print("No monitors initialized successfully!")
            return
        
        print(f"{'='*60}\n")
        
        # Run all monitors concurrently
        tasks = [self.monitor_account(monitor) for monitor in self.monitors]
        await asyncio.gather(*tasks)
    
    def start(self):
        """Start the multi-account monitor"""
        try:
            asyncio.run(self.start_async())
        except KeyboardInterrupt:
            print("\nStopping all monitors...")
            self.stop()
    
    def stop(self):
        """Stop all monitors"""
        self.running = False
        
        for monitor in self.monitors:
            try:
                monitor.stop()
            except:
                pass
        
        print("All monitors stopped.")


def main():
    """Entry point for multi-account monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Account Prop Risk Monitor")
    parser.add_argument(
        '--config',
        default='accounts.json',
        help='Path to accounts configuration file (default: accounts.json)'
    )
    
    args = parser.parse_args()
    
    if not Path(args.config).exists():
        print(f"Error: Configuration file '{args.config}' not found!")
        print("\nPlease create an accounts.json file based on accounts.json.example")
        print("Example:")
        print("  cp accounts.json.example accounts.json")
        print("  # Edit accounts.json with your account details")
        sys.exit(1)
    
    monitor = MultiAccountMonitor(config_file=args.config)
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop()


if __name__ == "__main__":
    main()
