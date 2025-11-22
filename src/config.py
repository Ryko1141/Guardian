"""
Configuration management for prop risk monitor
"""
import os
import json
from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class PropRules(BaseModel):
    """Risk rules for a prop trading firm"""
    
    name: str = Field(..., description="Name of the prop firm")
    max_daily_drawdown_pct: float = Field(..., description="Max daily drawdown as % of balance")
    max_total_drawdown_pct: float = Field(..., description="Max total drawdown as % of starting balance")
    max_risk_per_trade_pct: float = Field(..., description="Max risk per trade as % of balance")
    max_open_lots: float = Field(..., description="Maximum total lot size across all positions")
    max_positions: int = Field(default=10, description="Maximum number of concurrent positions")
    warn_buffer_pct: float = Field(default=0.8, description="Warning threshold (0.8 = warn at 80% of limit)")
    trading_days_only: bool = Field(default=True, description="Only count trading days for drawdown")
    require_stop_loss: bool = Field(default=True, description="All positions must have stop loss")
    max_leverage: Optional[float] = Field(default=None, description="Maximum allowed leverage")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Alpha Capital Group",
                "max_daily_drawdown_pct": 5.0,
                "max_total_drawdown_pct": 10.0,
                "max_risk_per_trade_pct": 1.0,
                "max_open_lots": 10.0,
                "max_positions": 10,
                "warn_buffer_pct": 0.8
            }
        }


class AccountConfig(BaseModel):
    """Configuration for a specific trading account"""
    
    label: str = Field(..., description="Human-readable label for this account")
    firm: str = Field(..., description="Prop firm name")
    platform: str = Field(..., description="Trading platform: 'ctrader' or 'mt5'")
    account_id: str = Field(..., description="Account ID or number")
    starting_balance: float = Field(..., description="Initial account balance")
    rules: PropRules = Field(..., description="Risk rules for this account")
    
    # Optional overrides
    telegram_chat_id: Optional[str] = Field(default=None, description="Override default Telegram chat")
    check_interval: int = Field(default=60, description="Check interval in seconds")
    enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "FTMO Challenge - 100k",
                "firm": "FTMO",
                "platform": "mt5",
                "account_id": "12345678",
                "starting_balance": 100000.0,
                "check_interval": 60,
                "enabled": True
            }
        }


# ============================================================
# Predefined Prop Firm Rules
# ============================================================

FTMO_RULES = PropRules(
    name="FTMO",
    max_daily_drawdown_pct=5.0,
    max_total_drawdown_pct=10.0,
    max_risk_per_trade_pct=1.0,
    max_open_lots=20.0,
    max_positions=10,
    warn_buffer_pct=0.8,
    trading_days_only=True,
    require_stop_loss=False
)

ALPHA_CAPITAL_RULES = PropRules(
    name="Alpha Capital Group",
    max_daily_drawdown_pct=5.0,
    max_total_drawdown_pct=10.0,
    max_risk_per_trade_pct=1.0,
    max_open_lots=10.0,
    max_positions=8,
    warn_buffer_pct=0.8,
    trading_days_only=True,
    require_stop_loss=True
)

FUNDED_TRADER_RULES = PropRules(
    name="The Funded Trader",
    max_daily_drawdown_pct=5.0,
    max_total_drawdown_pct=8.0,
    max_risk_per_trade_pct=2.0,
    max_open_lots=15.0,
    max_positions=12,
    warn_buffer_pct=0.75,
    trading_days_only=True,
    require_stop_loss=False
)

TOPSTEP_RULES = PropRules(
    name="TopstepFX",
    max_daily_drawdown_pct=4.0,
    max_total_drawdown_pct=6.0,
    max_risk_per_trade_pct=1.5,
    max_open_lots=12.0,
    max_positions=10,
    warn_buffer_pct=0.8,
    trading_days_only=True,
    require_stop_loss=False
)

FIVE_PERCENT_RULES = PropRules(
    name="5%ers",
    max_daily_drawdown_pct=5.0,
    max_total_drawdown_pct=10.0,
    max_risk_per_trade_pct=2.0,
    max_open_lots=20.0,
    max_positions=15,
    warn_buffer_pct=0.8,
    trading_days_only=False,  # 5%ers use calendar days
    require_stop_loss=False
)

# Map firm names to their rules
FIRM_RULES: Dict[str, PropRules] = {
    "ftmo": FTMO_RULES,
    "alpha": ALPHA_CAPITAL_RULES,
    "alpha_capital": ALPHA_CAPITAL_RULES,
    "funded_trader": FUNDED_TRADER_RULES,
    "the_funded_trader": FUNDED_TRADER_RULES,
    "topstep": TOPSTEP_RULES,
    "topstepfx": TOPSTEP_RULES,
    "5percenters": FIVE_PERCENT_RULES,
    "5%ers": FIVE_PERCENT_RULES,
}


class AccountManager:
    """Manages multiple trading accounts and their configurations"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize account manager
        
        Args:
            config_file: Path to JSON config file with account configurations
        """
        self.accounts: Dict[str, AccountConfig] = {}
        
        if config_file and Path(config_file).exists():
            self.load_from_file(config_file)
    
    def add_account(self, account: AccountConfig):
        """Add or update an account configuration"""
        self.accounts[account.account_id] = account
    
    def get_account(self, account_id: str) -> Optional[AccountConfig]:
        """Get account configuration by ID"""
        return self.accounts.get(account_id)
    
    def get_enabled_accounts(self) -> List[AccountConfig]:
        """Get all enabled accounts"""
        return [acc for acc in self.accounts.values() if acc.enabled]
    
    def load_from_file(self, filepath: str):
        """Load account configurations from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for acc_data in data.get("accounts", []):
            # Load rules from predefined or custom
            rules_data = acc_data.get("rules", {})
            if isinstance(rules_data, str):
                # Reference to predefined rules
                rules = FIRM_RULES.get(rules_data.lower())
                if not rules:
                    raise ValueError(f"Unknown firm rules: {rules_data}")
            else:
                # Custom rules
                rules = PropRules(**rules_data)
            
            account = AccountConfig(
                label=acc_data["label"],
                firm=acc_data["firm"],
                platform=acc_data["platform"],
                account_id=acc_data["account_id"],
                starting_balance=acc_data["starting_balance"],
                rules=rules,
                telegram_chat_id=acc_data.get("telegram_chat_id"),
                check_interval=acc_data.get("check_interval", 60),
                enabled=acc_data.get("enabled", True)
            )
            self.add_account(account)
    
    def save_to_file(self, filepath: str):
        """Save account configurations to JSON file"""
        data = {
            "accounts": [
                {
                    "label": acc.label,
                    "firm": acc.firm,
                    "platform": acc.platform,
                    "account_id": acc.account_id,
                    "starting_balance": acc.starting_balance,
                    "rules": acc.rules.dict(),
                    "telegram_chat_id": acc.telegram_chat_id,
                    "check_interval": acc.check_interval,
                    "enabled": acc.enabled
                }
                for acc in self.accounts.values()
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_account_from_env(self, firm_name: str = None) -> AccountConfig:
        """
        Create account config from environment variables
        
        Args:
            firm_name: Name of prop firm (to load predefined rules)
        """
        # Get rules from firm name or create from env vars
        if firm_name and firm_name.lower() in FIRM_RULES:
            rules = FIRM_RULES[firm_name.lower()]
        else:
            rules = PropRules(
                name=os.getenv("FIRM_NAME", "Custom"),
                max_daily_drawdown_pct=float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0")),
                max_total_drawdown_pct=float(os.getenv("MAX_TOTAL_DRAWDOWN_PERCENT", "10.0")),
                max_risk_per_trade_pct=float(os.getenv("MAX_POSITION_SIZE_PERCENT", "1.0")),
                max_open_lots=float(os.getenv("MAX_OPEN_LOTS", "10.0")),
                max_positions=int(os.getenv("MAX_POSITIONS", "10")),
                warn_buffer_pct=float(os.getenv("WARN_BUFFER_PCT", "0.8"))
            )
        
        account = AccountConfig(
            label=os.getenv("ACCOUNT_LABEL", "Default Account"),
            firm=os.getenv("FIRM_NAME", rules.name),
            platform=os.getenv("PLATFORM", "ctrader").lower(),
            account_id=os.getenv("ACCOUNT_ID"),
            starting_balance=float(os.getenv("STARTING_BALANCE", "10000.0")),
            rules=rules,
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            check_interval=int(os.getenv("CHECK_INTERVAL", "60")),
            enabled=os.getenv("ENABLED", "true").lower() == "true"
        )
        
        return account


class Config:
    """Application configuration"""
    
    # Trading platform selection
    PLATFORM = os.getenv("PLATFORM", "ctrader").lower()  # "ctrader" or "mt5"
    
    # cTrader API credentials
    CTRADER_CLIENT_ID = os.getenv("CTRADER_CLIENT_ID")
    CTRADER_CLIENT_SECRET = os.getenv("CTRADER_CLIENT_SECRET")
    CTRADER_ACCESS_TOKEN = os.getenv("CTRADER_ACCESS_TOKEN")
    
    # MetaTrader 5 credentials
    MT5_PASSWORD = os.getenv("MT5_PASSWORD")
    MT5_SERVER = os.getenv("MT5_SERVER")
    MT5_PATH = os.getenv("MT5_PATH")  # Optional: path to MT5 terminal
    
    # Account settings (used by both platforms)
    ACCOUNT_ID = os.getenv("ACCOUNT_ID")
    
    # Notification settings
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Monitoring rules
    MAX_DAILY_LOSS_PERCENT = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5.0"))
    MAX_POSITION_SIZE_PERCENT = float(os.getenv("MAX_POSITION_SIZE_PERCENT", "10.0"))
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        # Common required fields
        required = ["ACCOUNT_ID"]
        
        # Platform-specific required fields
        if cls.PLATFORM == "ctrader":
            required.extend([
                "CTRADER_CLIENT_ID",
                "CTRADER_CLIENT_SECRET",
                "CTRADER_ACCESS_TOKEN"
            ])
        elif cls.PLATFORM == "mt5":
            required.extend([
                "MT5_PASSWORD",
                "MT5_SERVER"
            ])
        else:
            raise ValueError(f"Invalid PLATFORM: {cls.PLATFORM}. Must be 'ctrader' or 'mt5'")
        
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
