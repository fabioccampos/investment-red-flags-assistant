from typing import Dict, List
from utils.sec_api import (
    get_yoy_comparison,
    get_latest_quarterly_values,
    extract_metric,
    get_company_info
)
from config import RED_FLAG_THRESHOLDS


class RedFlagAnalyzer:
    
    def __init__(self, company_data: Dict):

        self.company_data = company_data
        self.company_info = get_company_info(company_data)
        self.entity_name = self.company_info['name']
        
    def check_revenue_decline(self) -> Dict:
        """Red Flag 1: Revenue Decline"""
        current, previous = get_yoy_comparison(self.company_data, 'Revenues')
        
        if current is None or previous is None or previous == 0:
            return self._insufficient_data('revenue')
        
        change_pct = ((current - previous) / previous) * 100
        
        thresholds = RED_FLAG_THRESHOLDS['revenue_decline']
        
        if change_pct < thresholds['red']:
            severity = 'RED'
            message = f'Revenue declined {abs(change_pct):.1f}% YoY'
        elif change_pct < thresholds['yellow']:
            severity = 'YELLOW'
            message = f'Revenue declined {abs(change_pct):.1f}% YoY'
        else:
            severity = 'GREEN'
            if change_pct >= 0:
                message = f'Revenue grew {change_pct:.1f}% YoY'
            else:
                message = f'Revenue declined only {abs(change_pct):.1f}% YoY'
        
        return {
            'status': 'OK',
            'severity': severity,
            'message': message,
            'current_value': current,
            'previous_value': previous,
            'change_pct': change_pct,
            'metric': 'Revenue (YoY)'
        }
    
    def check_margin_compression(self) -> Dict:
        """Red Flag 2: Margin Compression"""
        revenue_curr, revenue_prev = get_yoy_comparison(self.company_data, 'Revenues')
        opinc_curr, opinc_prev = get_yoy_comparison(self.company_data, 'OperatingIncome')
        
        if None in [revenue_curr, revenue_prev, opinc_curr, opinc_prev]:
            return self._insufficient_data('operating margin')
        
        if revenue_curr == 0 or revenue_prev == 0:
            return self._insufficient_data('margin (revenue zero)')
        
        margin_curr = (opinc_curr / revenue_curr) * 100
        margin_prev = (opinc_prev / revenue_prev) * 100
        margin_change = margin_curr - margin_prev
        
        thresholds = RED_FLAG_THRESHOLDS['margin_compression']
        
        if margin_change < thresholds['red']:
            severity = 'RED'
            message = f'Operating margin declined {abs(margin_change):.1f}pp'
        elif margin_change < thresholds['yellow']:
            severity = 'YELLOW'
            message = f'Operating margin declined {abs(margin_change):.1f}pp'
        else:
            severity = 'GREEN'
            if margin_change >= 0:
                message = f'Operating margin improved {margin_change:.1f}pp'
            else:
                message = f'Margin declined only {abs(margin_change):.1f}pp'
        
        return {
            'status': 'OK',
            'severity': severity,
            'message': message,
            'current_margin': margin_curr,
            'previous_margin': margin_prev,
            'change_pp': margin_change,
            'metric': 'Operating Margin'
        }
    
    def check_debt_explosion(self) -> Dict:
        """Red Flag 3: Debt Explosion"""
        # Try getting long term debt
        lt_debt_curr, lt_debt_prev = get_yoy_comparison(self.company_data, 'LongTermDebt')
        curr_debt_curr, curr_debt_prev = get_yoy_comparison(self.company_data, 'CurrentDebt')
        
        # Add up debts
        total_debt_curr = (lt_debt_curr or 0) + (curr_debt_curr or 0)
        total_debt_prev = (lt_debt_prev or 0) + (curr_debt_prev or 0)
        
        if total_debt_curr == 0 or total_debt_prev == 0:
            return self._insufficient_data('debt')
        
        debt_change = ((total_debt_curr - total_debt_prev) / total_debt_prev) * 100
        
        thresholds = RED_FLAG_THRESHOLDS['debt_explosion']
        
        if debt_change > thresholds['red']:
            severity = 'RED'
            message = f'Total debt increased {debt_change:.1f}%'
        elif debt_change > thresholds['yellow']:
            severity = 'YELLOW'
            message = f'Total debt increased {debt_change:.1f}%'
        else:
            severity = 'GREEN'
            if debt_change < 0:
                message = f'Total debt decreased {abs(debt_change):.1f}%'
            else:
                message = f'Debt increased only {debt_change:.1f}%'
        
        return {
            'status': 'OK',
            'severity': severity,
            'message': message,
            'current_debt': total_debt_curr,
            'previous_debt': total_debt_prev,
            'change_pct': debt_change,
            'metric': 'Total Debt (YoY)'
        }
    
    def check_negative_cash_flow(self) -> Dict:
        """Red Flag 4: Negative Operating Cash Flow"""
        cash_flows = get_latest_quarterly_values(
            self.company_data, 
            'OperatingCashFlow', 
            periods=4
        )
        
        if len(cash_flows) < 2:
            return self._insufficient_data('cash flow')
        
        # Count consecutives negatives quarters
        negative_quarters = 0
        for cf in cash_flows:
            if cf < 0:
                negative_quarters += 1
            else:
                break
        
        thresholds = RED_FLAG_THRESHOLDS['negative_cash_flow']
        
        if negative_quarters >= thresholds['red']:
            severity = 'RED'
            message = f'{negative_quarters} consecutive quarters with negative OCF'
        elif negative_quarters >= thresholds['yellow']:
            severity = 'YELLOW'
            message = f'{negative_quarters} quarters with negative OCF'
        else:
            severity = 'GREEN'
            message = f'Operating cash flow is positive'
        
        return {
            'status': 'OK',
            'severity': severity,
            'message': message,
            'negative_quarters': negative_quarters,
            'latest_cash_flows': cash_flows[:4],
            'metric': 'Operating Cash Flow'
        }
    
    def check_liquidity_deterioration(self) -> Dict:
        """Red Flag 5: Liquidity Deterioration"""
        curr_assets_curr, curr_assets_prev = get_yoy_comparison(
            self.company_data, 'CurrentAssets'
        )
        curr_liab_curr, curr_liab_prev = get_yoy_comparison(
            self.company_data, 'CurrentLiabilities'
        )
        
        if None in [curr_assets_curr, curr_liab_curr]:
            return self._insufficient_data('liquidity')
        
        if curr_liab_curr == 0:
            return self._insufficient_data('liquidity (liabilities zero)')
        
        current_ratio = curr_assets_curr / curr_liab_curr
        
        thresholds = RED_FLAG_THRESHOLDS['liquidity_deterioration']
        
        if current_ratio < thresholds['red']:
            severity = 'RED'
            message = f'Current Ratio = {current_ratio:.2f} (< 1.0) - Liquidity risk'
        elif current_ratio < thresholds['yellow']:
            severity = 'YELLOW'
            message = f'Current Ratio = {current_ratio:.2f} - Tight liquidity'
        else:
            severity = 'GREEN'
            message = f'Current Ratio = {current_ratio:.2f} - Healthy liquidity'
        
        return {
            'status': 'OK',
            'severity': severity,
            'message': message,
            'current_ratio': current_ratio,
            'metric': 'Current Ratio'
        }
    
    def analyze_all(self) -> Dict:

        results = {
            'entity_name': self.entity_name,
            'cik': self.company_info['cik'],
            'red_flags': {
                'revenue_decline': self.check_revenue_decline(),
                'margin_compression': self.check_margin_compression(),
                'debt_explosion': self.check_debt_explosion(),
                'negative_cash_flow': self.check_negative_cash_flow(),
                'liquidity_deterioration': self.check_liquidity_deterioration()
            }
        }
        
        # Total score
        severities = [
            rf['severity'] 
            for rf in results['red_flags'].values() 
            if rf.get('severity') != 'UNKNOWN'
        ]
        
        red_count = severities.count('RED')
        yellow_count = severities.count('YELLOW')
        green_count = severities.count('GREEN')
        
        # Evaluation
        if red_count >= 2:
            overall = 'RED'
        elif red_count >= 1 or yellow_count >= 3:
            overall = 'YELLOW'
        else:
            overall = 'GREEN'
        
        results['overall_assessment'] = overall
        results['summary'] = {
            'red_flags_count': red_count,
            'yellow_flags_count': yellow_count,
            'green_flags_count': green_count
        }
        
        return results
    
    def _insufficient_data(self, field_name: str) -> Dict:
        """Helper to return insufficient data response"""
        return {
            'status': 'INSUFFICIENT_DATA',
            'severity': 'UNKNOWN',
            'message': f'Insufficient data for {field_name} analysis',
            'metric': field_name
        }
