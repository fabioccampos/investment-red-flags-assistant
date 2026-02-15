SEC_BASE_URL = 'https://data.sec.gov'
SEC_HEADERS = {
    'User-Agent': 'SEC-RedFlags-App academic-research@example.com'
}


TICKER_TO_CIK = {
    'AAPL': '0000320193',   # Apple
    'MSFT': '0000789019',   # Microsoft
    'TSLA': '0001318605',   # Tesla
    'AMZN': '0001018724',   # Amazon
    'GOOGL': '0001652044',  # Alphabet
    'META': '0001326801',   # Meta
    'NVDA': '0001045810',   # Nvidia
    'JPM': '0000019617',    # JPMorgan
    'V': '0001403161',      # Visa
    'WMT': '0000104169',    # Walmart
    'JNJ': '0000200406',    # Johnson & Johnson
    'PG': '0000080424',     # Procter & Gamble
    'DIS': '0001001039',    # Disney
    'NFLX': '0001065280',   # Netflix
    'INTC': '0000050863',   # Intel
    'AMD': '0000002488',    # AMD
    'BA': '0000012927',     # Boeing
    'GE': '0000040545',     # General Electric
    'F': '0000037996',      # Ford
    'GM': '0001467858',     # General Motors
}


FIELD_MAPPINGS = {
    'Revenues': [
        'RevenueFromContractWithCustomerExcludingAssessedTax',  # Pós-2018 (ASC 606)
        'Revenues',
        'SalesRevenueNet',
        'RevenueFromContractWithCustomerIncludingAssessedTax'
    ],
    'OperatingIncome': [
        'OperatingIncomeLoss',
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
    ],
    'TotalAssets': [
        'Assets',
    ],
    'CurrentAssets': [
        'AssetsCurrent'
    ],
    'CurrentLiabilities': [
        'LiabilitiesCurrent'
    ],
    'LongTermDebt': [
        'LongTermDebt',
        'LongTermDebtNoncurrent',
        'DebtLongTerm'
    ],
    'CurrentDebt': [
        'LongTermDebtCurrent',
        'DebtCurrent',
        'ShortTermBorrowings'
    ],
    'OperatingCashFlow': [
        'NetCashProvidedByUsedInOperatingActivities',
        'CashProvidedByUsedInOperatingActivities'
    ],
    'StockholdersEquity': [
        'StockholdersEquity',
        'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
    ]
}


RED_FLAG_THRESHOLDS = {
    'revenue_decline': {
        'red': -15.0,     # Dip > 15%
        'yellow': -5.0     # Dip 5-15%
    },
    'margin_compression': {
        'red': -5.0,      # Dip > 5pp
        'yellow': -2.0     # Dip 2-5pp
    },
    'debt_explosion': {
        'red': 50.0,      # Rise > 50%
        'yellow': 20.0     # Rise 20-50%
    },
    'negative_cash_flow': {
        'red': 3,         # 3+ negative quarters
        'yellow': 2        # 2 negative quarters
    },
    'liquidity_deterioration': {
        'red': 1.0,       # Current Ratio < 1.0
        'yellow': 1.2      # Current Ratio 1.0-1.2
    }
}


HF_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
HF_API_URL = f"https://router.huggingface.co/models/{HF_MODEL}"
HF_MAX_TOKENS = 500
HF_TEMPERATURE = 0.7


APP_TITLE = "Red Flags Assistant"
APP_SUBTITLE = "Financial Stress Signal Detection for Public Companies"
DISCLAIMER = """
**IMPORTANT DISCLAIMER**

This tool is for **transparency and monitoring purposes only**. 

- NOT financial advice
- NOT for trading decisions
- NOT a substitute for professional analysis

The analysis is based on automated XBRL data extraction and AI-generated interpretations.
Always verify findings with original SEC filings and consult qualified professionals.
"""


COLORS = {
    'RED': '#d32f2f',
    'YELLOW': '#ffa726',
    'GREEN': '#66bb6a',
    'UNKNOWN': '#bdbdbd'
}

EMOJI = {
    'RED': '🔴',
    'YELLOW': '🟡',
    'GREEN': '🟢',
    'UNKNOWN': '⚪'
}
