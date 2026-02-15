import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple
from config import SEC_BASE_URL, SEC_HEADERS, TICKER_TO_CIK, FIELD_MAPPINGS


def get_company_cik(ticker: str) -> Optional[str]:

    return TICKER_TO_CIK.get(ticker.upper())


def fetch_company_facts(cik: str) -> Optional[Dict]:

    url = f'{SEC_BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json'
    
    try:
        response = requests.get(url, headers=SEC_HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


def extract_field_values_smart(
    company_data: Dict, 
    field_names: List[str], 
    unit: str = 'USD'
) -> pd.DataFrame:

    all_data = []
    
    for field_name in field_names:
        try:
            facts = company_data['facts']['us-gaap'][field_name]['units'][unit]
            df = pd.DataFrame(facts)
            df['field_source'] = field_name
            all_data.append(df)
        except (KeyError, TypeError):
            continue
    
    if not all_data:
        return pd.DataFrame()
    
    # Combine DataFrames
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Filter  10-K e 10-Q (main reports)
    combined_df = combined_df[combined_df['form'].isin(['10-K', '10-Q'])].copy()
    
    # Convert
    combined_df['end'] = pd.to_datetime(combined_df['end'])
    
    # Date ordering
    combined_df = combined_df.sort_values('end', ascending=False)
    
    # Remove duplicates
    combined_df = combined_df.drop_duplicates(subset=['end'], keep='first')
    
    return combined_df[['end', 'val', 'fy', 'fp', 'form', 'field_source']].reset_index(drop=True)


def extract_metric(
    company_data: Dict, 
    metric_name: str, 
    verbose: bool = False
) -> pd.DataFrame:

    if metric_name not in FIELD_MAPPINGS:
        if verbose:
            print(f"Metric '{metric_name}' not mapped. Trying direct field...")
        return extract_field_values_smart(company_data, [metric_name])
    
    field_names = FIELD_MAPPINGS[metric_name]
    df = extract_field_values_smart(company_data, field_names)
    
    if not df.empty and verbose:
        sources = df['field_source'].unique()
        print(f"{metric_name}: {len(df)} periods using {', '.join(sources)}")
    
    return df


def get_yoy_comparison(
    company_data: Dict, 
    metric_name: str
) -> Tuple[Optional[float], Optional[float]]:

    df = extract_metric(company_data, metric_name)
    
    if df.empty or len(df) < 2:
        return None, None
    
    current = df.iloc[0]['val']
    current_fp = df.iloc[0]['fp']
    current_fy = df.iloc[0]['fy']
    
    previous = None
    for i in range(1, len(df)):
        row = df.iloc[i]
        if row['fp'] == current_fp and row['fy'] == (current_fy - 1):
            previous = row['val']
            break
    
    if previous is None and len(df) >= 5:
        previous = df.iloc[4]['val']
    
    return current, previous


def get_latest_quarterly_values(
    company_data: Dict, 
    metric_name: str, 
    periods: int = 4
) -> List[float]:

    df = extract_metric(company_data, metric_name)
    
    if df.empty:
        return []
    
    quarterly = df[df['form'] == '10-Q'].head(periods)
    
    return quarterly['val'].tolist()


def get_company_info(company_data: Dict) -> Dict[str, str]:

    return {
        'name': company_data.get('entityName', 'Unknown'),
        'cik': company_data.get('cik', 'Unknown')
    }
