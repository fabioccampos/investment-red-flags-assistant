import streamlit as st
from utils import (
    get_company_cik,
    fetch_company_facts,
    RedFlagAnalyzer,
    generate_analysis_narrative
)
from utils.llm_integration_openai import generate_analysis_narrative
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    DISCLAIMER,
    COLORS,
    EMOJI,
    TICKER_TO_CIK
)

# Configuração da página
st.set_page_config(
    page_title="Red Flags Assistant",
    page_icon="🔴",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS customizado para interface minimalista
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .signal-box {
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .red-signal {
        background-color: #ffebee;
        color: #c62828;
    }
    .yellow-signal {
        background-color: #fff3e0;
        color: #ef6c00;
    }
    .green-signal {
        background-color: #e8f5e9;
        color: #2e7d32;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .disclaimer-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        border-left: 4px solid #757575;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: #000000;
    }
    .ai-narrative {
        background-color: #000000;
        padding: 1.5rem;
        border-radius: 5px;
        margin: 1rem 0;
        border-left: 4px solid #1976d2;
    }
</style>
""", unsafe_allow_html=True)


def main():
    
    # Header
    st.markdown(f"<div class='main-header'><h1>Red Flags Assistant</h1><p>{APP_SUBTITLE}</p></div>", 
                unsafe_allow_html=True)
    
    # Input Section
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker_input = st.text_input(
            "Enter Stock Ticker",
            placeholder="e.g., AAPL, TSLA, MSFT",
            help="Enter a valid US stock ticker symbol"
        ).upper()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacer
        analyze_button = st.button("Analyze", use_container_width=True)
    
    # Mostrar tickers disponíveis
    with st.expander("Available Tickers"):
        tickers_list = ", ".join(sorted(TICKER_TO_CIK.keys()))
        st.text(tickers_list)
        st.caption(f"Total: {len(TICKER_TO_CIK)} companies")
    
    # Processar análise
    if analyze_button:
        if not ticker_input:
            st.warning("Please enter a ticker symbol")
            return
        
        with st.spinner(f"Analyzing {ticker_input}..."):
            run_analysis(ticker_input)
    
    # Disclaimer sempre visível
    st.markdown("---")
    st.markdown(f"<div class='disclaimer-box'>{DISCLAIMER}</div>", 
                unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.caption("Data source: SEC EDGAR | Analysis: Automated XBRL + AI")


def run_analysis(ticker: str):

    cik = get_company_cik(ticker)
    if not cik:
        st.error(f"Ticker '{ticker}' not found in database")
        st.info("Tip: Check the available tickers list above")
        return
    
    try:
        company_data = fetch_company_facts(cik)
        
        if not company_data:
            st.error("Failed to fetch data from SEC. Please try again.")
            return
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return
    
    try:
        analyzer = RedFlagAnalyzer(company_data)
        results = analyzer.analyze_all()
        
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return
    
    display_results(results)


def display_results(results: dict):

    company_name = results['entity_name']
    overall = results['overall_assessment']
    summary = results['summary']
    
    st.markdown("### Analysis Results")
    
    signal_class = f"{overall.lower()}-signal"
    signal_emoji = EMOJI[overall]
    
    st.markdown(
        f"<div class='signal-box {signal_class}'>"
        f"{company_name}<br>"
        f"<small style='font-size: 1.2rem;'>{signal_emoji} {overall} Flag</small>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Red Flags", summary['red_flags_count'])
    with col2:
        st.metric("Yellow Flags", summary['yellow_flags_count'])
    with col3:
        st.metric("Green Flags", summary['green_flags_count'])
    
    st.markdown("---")

    with st.spinner("Generating analysis..."):
        try:
            print("\n" + "="*60)
            print("DEBUG: calling generate_analysis_narrative")
            print("="*60)
            
            narrative = generate_analysis_narrative(results)
            
            print(f"DEBUG: Narrative received. Type: {type(narrative)}")
            print(f"DEBUG: Size: {len(narrative) if narrative else 0} caracteres")
            print(f"DEBUG: First 100 chars: {narrative[:100] if narrative else 'Empty'}")
            print("="*60 + "\n")
            
            st.markdown(f"<div class='ai-narrative'>{narrative}</div>", unsafe_allow_html=True)
            
            print("DEBUG: Narrative successful\n")
            
        except Exception as e:
            print("\n" + "="*60)
            print(f"DEBUG: exception")
            print(f"Type: {type(e)}")
            print(f"Message: {str(e)}")
            print("="*60 + "\n")
            
            st.warning(f"Could not generate AI narrative: {str(e)}")
            st.info("Showing rule-based analysis instead...")
            from utils.llm_integration import generate_rule_based_analysis
            narrative = generate_rule_based_analysis(results)
            st.markdown(f"<div class='ai-narrative'>{narrative}</div>", unsafe_allow_html=True)
    
    # Red Flags Breakdown
    st.markdown("---")
    st.markdown("### Breakdown")
    
    flag_titles = {
        'revenue_decline': 'Revenue Decline',
        'margin_compression': 'Margin Compression',
        'debt_explosion': 'Debt Explosion',
        'negative_cash_flow': 'Negative Cash Flow',
        'liquidity_deterioration': 'Liquidity Deterioration'
    }
    
    for flag_key, flag_title in flag_titles.items():
        result = results['red_flags'][flag_key]
        
        if result['status'] == 'INSUFFICIENT_DATA':
            st.info(f"{flag_title}: {result['message']}")
            continue
        
        severity = result['severity']
        color = COLORS[severity]
        emoji = EMOJI[severity]
        
        st.markdown(
            f"<div class='metric-card' style='border-left-color: {color};'>"
            f"<strong>{emoji} {flag_title}</strong><br>"
            f"{result['message']}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    # Evidence Links
    st.markdown("---")
    st.markdown("### Verify Evidence")
    
    cik = results['cik']
    sec_link = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-&dateb=&owner=exclude&count=40"
    
    st.markdown(
        f"[View SEC Filings]({sec_link}) | "
        f"[Company Facts JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json)"
    )
    
    st.caption("Always verify automated findings with original SEC documents")


if __name__ == "__main__":
    main()
