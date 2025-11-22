"""
Risk monitoring rules and validators
"""
from typing import List, Optional
from datetime import datetime
from src.models import AccountSnapshot, RuleViolation
from src.config import PropRules, Config


class RiskRuleEngine:
    """Engine for evaluating risk rules against account state"""
    
    def __init__(self, prop_rules: Optional[PropRules] = None, starting_balance: Optional[float] = None):
        """
        Initialize rule engine
        
        Args:
            prop_rules: PropRules object with firm-specific rules (if None, uses Config)
            starting_balance: Starting account balance for total drawdown calculation
        """
        if prop_rules:
            self.rules = prop_rules
        else:
            # Fallback to legacy Config for backwards compatibility
            self.rules = PropRules(
                name="Legacy",
                max_daily_drawdown_pct=Config.MAX_DAILY_LOSS_PERCENT,
                max_total_drawdown_pct=Config.MAX_DAILY_LOSS_PERCENT * 2,
                max_risk_per_trade_pct=Config.MAX_POSITION_SIZE_PERCENT,
                max_open_lots=100.0,
                max_positions=20
            )
        
        self.starting_balance = starting_balance or 10000.0
        self.highest_balance = starting_balance or 10000.0  # Track for trailing drawdown
    
    def evaluate(self, snapshot: AccountSnapshot) -> List[RuleViolation]:
        """Evaluate all rules against account snapshot"""
        violations = []
        
        # Update highest balance for trailing drawdown
        if snapshot.balance > self.highest_balance:
            self.highest_balance = snapshot.balance
        
        # Check daily drawdown limit
        daily_dd_violation = self._check_daily_drawdown(snapshot)
        if daily_dd_violation:
            violations.append(daily_dd_violation)
        
        # Check total drawdown limit
        total_dd_violation = self._check_total_drawdown(snapshot)
        if total_dd_violation:
            violations.append(total_dd_violation)
        
        # Check position size limits (risk per trade)
        position_violations = self._check_position_sizes(snapshot)
        violations.extend(position_violations)
        
        # Check total lot size limit
        lot_violation = self._check_total_lots(snapshot)
        if lot_violation:
            violations.append(lot_violation)
        
        # Check number of positions
        position_count_violation = self._check_position_count(snapshot)
        if position_count_violation:
            violations.append(position_count_violation)
        
        # Check stop loss requirement
        if self.rules.require_stop_loss:
            sl_violations = self._check_stop_losses(snapshot)
            violations.extend(sl_violations)
        
        # Check margin levels
        margin_violation = self._check_margin_level(snapshot)
        if margin_violation:
            violations.append(margin_violation)
        
        return violations
    
    def _check_daily_drawdown(self, snapshot: AccountSnapshot) -> Optional[RuleViolation]:
        """Check if daily drawdown exceeds maximum threshold"""
        daily_loss_pct = abs(snapshot.daily_loss_percent)
        warning_threshold = self.rules.max_daily_drawdown_pct * self.rules.warn_buffer_pct
        
        # Critical violation
        if daily_loss_pct >= self.rules.max_daily_drawdown_pct:
            return RuleViolation(
                rule_name="Daily Drawdown Limit",
                severity="critical",
                message=f"🚨 CRITICAL: Daily drawdown of {daily_loss_pct:.2f}% exceeds {self.rules.name} limit of {self.rules.max_daily_drawdown_pct}%!",
                timestamp=datetime.now(),
                value=daily_loss_pct,
                threshold=self.rules.max_daily_drawdown_pct
            )
        
        # Warning
        elif daily_loss_pct >= warning_threshold:
            return RuleViolation(
                rule_name="Daily Drawdown Warning",
                severity="warning",
                message=f"⚠️ WARNING: Daily drawdown of {daily_loss_pct:.2f}% approaching {self.rules.name} limit of {self.rules.max_daily_drawdown_pct}%",
                timestamp=datetime.now(),
                value=daily_loss_pct,
                threshold=warning_threshold
            )
        
        return None
    
    def _check_total_drawdown(self, snapshot: AccountSnapshot) -> Optional[RuleViolation]:
        """Check if total drawdown from starting balance exceeds limit"""
        total_dd_pct = ((self.starting_balance - snapshot.balance) / self.starting_balance) * 100
        warning_threshold = self.rules.max_total_drawdown_pct * self.rules.warn_buffer_pct
        
        if total_dd_pct < 0:  # Account is profitable
            return None
        
        # Critical violation
        if total_dd_pct >= self.rules.max_total_drawdown_pct:
            return RuleViolation(
                rule_name="Total Drawdown Limit",
                severity="critical",
                message=f"🚨 CRITICAL: Total drawdown of {total_dd_pct:.2f}% exceeds {self.rules.name} limit of {self.rules.max_total_drawdown_pct}%!",
                timestamp=datetime.now(),
                value=total_dd_pct,
                threshold=self.rules.max_total_drawdown_pct
            )
        
        # Warning
        elif total_dd_pct >= warning_threshold:
            return RuleViolation(
                rule_name="Total Drawdown Warning",
                severity="warning",
                message=f"⚠️ WARNING: Total drawdown of {total_dd_pct:.2f}% approaching {self.rules.name} limit of {self.rules.max_total_drawdown_pct}%",
                timestamp=datetime.now(),
                value=total_dd_pct,
                threshold=warning_threshold
            )
        
        return None
    
    def _check_position_sizes(self, snapshot: AccountSnapshot) -> List[RuleViolation]:
        """Check if any position exceeds maximum risk per trade"""
        violations = []
        warning_threshold = self.rules.max_risk_per_trade_pct * self.rules.warn_buffer_pct
        
        for position in snapshot.positions:
            # Calculate position risk as percentage of balance
            position_value = abs(position.volume * position.current_price)
            position_pct = (position_value / snapshot.balance) * 100
            
            # Critical violation
            if position_pct >= self.rules.max_risk_per_trade_pct:
                violations.append(RuleViolation(
                    rule_name="Risk Per Trade Limit",
                    severity="critical",
                    message=f"🚨 Position {position.symbol} risk of {position_pct:.2f}% exceeds {self.rules.name} limit of {self.rules.max_risk_per_trade_pct}%!",
                    timestamp=datetime.now(),
                    value=position_pct,
                    threshold=self.rules.max_risk_per_trade_pct
                ))
            
            # Warning
            elif position_pct >= warning_threshold:
                violations.append(RuleViolation(
                    rule_name="Risk Per Trade Warning",
                    severity="warning",
                    message=f"⚠️ Position {position.symbol} risk of {position_pct:.2f}% approaching {self.rules.name} limit of {self.rules.max_risk_per_trade_pct}%",
                    timestamp=datetime.now(),
                    value=position_pct,
                    threshold=warning_threshold
                ))
        
        return violations
    
    def _check_total_lots(self, snapshot: AccountSnapshot) -> Optional[RuleViolation]:
        """Check if total lot size across all positions exceeds limit"""
        total_lots = sum(abs(pos.volume) for pos in snapshot.positions)
        warning_threshold = self.rules.max_open_lots * self.rules.warn_buffer_pct
        
        # Critical violation
        if total_lots >= self.rules.max_open_lots:
            return RuleViolation(
                rule_name="Total Lot Size Limit",
                severity="critical",
                message=f"🚨 Total lot size of {total_lots:.2f} exceeds {self.rules.name} limit of {self.rules.max_open_lots}!",
                timestamp=datetime.now(),
                value=total_lots,
                threshold=self.rules.max_open_lots
            )
        
        # Warning
        elif total_lots >= warning_threshold:
            return RuleViolation(
                rule_name="Total Lot Size Warning",
                severity="warning",
                message=f"⚠️ Total lot size of {total_lots:.2f} approaching {self.rules.name} limit of {self.rules.max_open_lots}",
                timestamp=datetime.now(),
                value=total_lots,
                threshold=warning_threshold
            )
        
        return None
    
    def _check_position_count(self, snapshot: AccountSnapshot) -> Optional[RuleViolation]:
        """Check if number of open positions exceeds limit"""
        position_count = len(snapshot.positions)
        
        if position_count > self.rules.max_positions:
            return RuleViolation(
                rule_name="Position Count Limit",
                severity="warning",
                message=f"⚠️ {position_count} open positions exceeds {self.rules.name} limit of {self.rules.max_positions}",
                timestamp=datetime.now(),
                value=float(position_count),
                threshold=float(self.rules.max_positions)
            )
        
        return None
    
    def _check_stop_losses(self, snapshot: AccountSnapshot) -> List[RuleViolation]:
        """Check if all positions have stop losses (if required by firm)"""
        violations = []
        
        for position in snapshot.positions:
            # Note: This check assumes positions have an 'sl' attribute
            # You may need to extend the Position model to include stop loss
            if not hasattr(position, 'stop_loss') or position.stop_loss == 0:
                violations.append(RuleViolation(
                    rule_name="Missing Stop Loss",
                    severity="warning",
                    message=f"⚠️ Position {position.symbol} (ticket {position.position_id}) missing required stop loss per {self.rules.name} rules",
                    timestamp=datetime.now(),
                    value=0.0,
                    threshold=1.0
                ))
        
        return violations
    
    def _check_margin_level(self, snapshot: AccountSnapshot) -> Optional[RuleViolation]:
        """Check if margin level is critically low"""
        if snapshot.margin_used == 0:
            return None
        
        margin_level = (snapshot.margin_available / snapshot.margin_used * 100)
        
        if margin_level < 50:  # Critical threshold
            return RuleViolation(
                rule_name="Low Margin Level",
                severity="critical",
                message=f"🚨 CRITICAL: Margin level critically low at {margin_level:.2f}%",
                timestamp=datetime.now(),
                value=margin_level,
                threshold=50.0
            )
        elif margin_level < 100:  # Warning threshold
            return RuleViolation(
                rule_name="Low Margin Level",
                severity="warning",
                message=f"⚠️ WARNING: Margin level low at {margin_level:.2f}%",
                timestamp=datetime.now(),
                value=margin_level,
                threshold=100.0
            )
        
        return None
