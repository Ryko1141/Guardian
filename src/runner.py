"""
Main runner for the prop risk monitor
"""
import os
import time
from datetime import datetime
from src.config import Config, AccountConfig, AccountManager
from src.models import AccountSnapshot, Position
from src.rules import RiskRuleEngine
from src.notifier import Notifier


class RiskMonitor:
    """Main monitoring service"""
    
    def __init__(self, account_config: AccountConfig = None, check_interval: int = None):
        """
        Initialize the risk monitor
        
        Args:
            account_config: AccountConfig object with account and rules (if None, uses env vars)
            check_interval: Time between checks in seconds (overrides account_config)
        """
        # Load account configuration
        if account_config:
            self.account_config = account_config
        else:
            # Create from environment variables for backwards compatibility
            Config.validate()
            firm_name = os.getenv("FIRM_NAME")
            manager = AccountManager()
            self.account_config = manager.create_account_from_env(firm_name)
        
        # Override check interval if provided
        if check_interval:
            self.account_config.check_interval = check_interval
        
        # Initialize the appropriate client based on platform
        if self.account_config.platform == "ctrader":
            from src.ctrader_client import CTraderClient
            self.client = CTraderClient(
                account_id=self.account_config.account_id
            )
            print(f"Using cTrader platform for {self.account_config.label}")
        elif self.account_config.platform == "mt5":
            from src.mt5_client import MT5Client
            self.client = MT5Client(
                account_number=int(self.account_config.account_id)
            )
            # Connect to MT5 terminal
            if not self.client.connect():
                raise ConnectionError("Failed to connect to MT5")
            print(f"Using MetaTrader 5 platform for {self.account_config.label}")
        else:
            raise ValueError(f"Unsupported platform: {self.account_config.platform}")
        
        # Initialize rule engine with prop firm rules
        self.rule_engine = RiskRuleEngine(
            prop_rules=self.account_config.rules,
            starting_balance=self.account_config.starting_balance
        )
        
        # Initialize notifier (use account-specific chat if provided)
        self.notifier = Notifier(
            telegram_chat_id=self.account_config.telegram_chat_id
        )
        
        self.running = False
        
        # Send startup notification
        self.notifier.send_status(
            f"🚀 Risk Monitor Started\n"
            f"Account: {self.account_config.label}\n"
            f"Firm: {self.account_config.firm}\n"
            f"Platform: {self.account_config.platform.upper()}\n"
            f"Starting Balance: ${self.account_config.starting_balance:,.2f}\n"
            f"Check Interval: {self.account_config.check_interval}s"
        )
    
    def _create_snapshot(self) -> AccountSnapshot:
        """Create an account snapshot from current API data"""
        # Use the enhanced get_account_snapshot method
        return self.client.get_account_snapshot()
    
    def check_once(self):
        """Perform a single monitoring check"""
        try:
            snapshot = self._create_snapshot()
            violations = self.rule_engine.evaluate(snapshot)
            
            if violations:
                self.notifier.send_violations(violations)
            
            print(f"[{snapshot.timestamp}] Check complete - Equity: ${snapshot.equity:.2f}, P&L: ${snapshot.total_profit_loss:.2f}, Violations: {len(violations)}")
            
        except Exception as e:
            print(f"Error during check: {e}")
            self.notifier.send_status(f"Error during monitoring: {str(e)}")
    
    def start(self):
        """Start the monitoring loop"""
        self.running = True
        
        print(f"Starting risk monitor for {self.account_config.label}...")
        print(f"Firm: {self.account_config.firm} ({self.account_config.rules.name})")
        print(f"Check interval: {self.account_config.check_interval}s")
        
        while self.running:
            self.check_once()
            time.sleep(self.account_config.check_interval)
    
    def stop(self):
        """Stop the monitoring loop"""
        self.running = False
        self.notifier.send_status("Risk monitor stopped")
        print("Risk monitor stopped")


def main():
    """Entry point for the application"""
    monitor = RiskMonitor(check_interval=60)
    
    try:
        monitor.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        monitor.stop()


if __name__ == "__main__":
    main()
