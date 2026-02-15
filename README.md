# Investment Red Flags Assistant

**Financial Stress Signal Detection for Public Companies**

A transparency and monitoring tool that analyzes SEC XBRL filings to detect early warning signs of accounting stress in public companies.

---

## Deployment to Hugging Face Spaces

The project is currently deployed on a free Hugging Face Space
Link: https://huggingface.co/spaces/Fabeats/investment-red-flags-assistance

## Features

- **5 Red Flag Indicators:**
  - Revenue Decline
  - Margin Compression  
  - Debt Explosion
  - Negative Cash Flow
  - Liquidity Deterioration

- **AI-Powered Explanations:** Uses OpenAI gpt-4o-mini to generate accessible narratives

- **Minimalista Interface:** Clean, focused on results

- **Evidence-Based:** Direct links to SEC filings for verification

---

## Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd sec-red-flags-app
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the app**
```bash
streamlit run app.py
```

4. **Open browser**
Navigate to `http://localhost:8501`

---

## 📊 How It Works

```
Input (Ticker) → SEC EDGAR API → XBRL Extraction → 
Red Flag Analysis → LLM Narrative → Output (Signal + Evidence)
```

### Data Source
- **SEC EDGAR API** (no API key required)
- Automatically handles field changes (e.g., ASC 606 revenue recognition)
- Uses multiple alternative XBRL fields for robustness

### Analysis Logic
Each red flag uses specific thresholds:
- **Revenue:** < -15% YoY = RED, -5% to -15% = AMBER
- **Margin:** < -5pp = RED, -2pp to -5pp = AMBER  
- **Debt:** > +50% YoY = RED, +20% to +50% = AMBER
- **Cash Flow:** 3+ negative quarters = RED, 2 = AMBER
- **Liquidity:** Current Ratio < 1.0 = RED, 1.0-1.2 = AMBER

---

## Available Tickers

Currently supports 20 major companies:

**Tech:** AAPL, MSFT, GOOGL, META, NVDA, TSLA, NFLX, INTC, AMD

**Finance:** JPM, V

**Consumer:** WMT, PG, JNJ, DIS

**Other:** AMZN, BA, GE, F, GM

To add more tickers, update `TICKER_TO_CIK` in `config.py`

---

## Technical Details

### Architecture

- **Frontend:** Streamlit (Python)
- **Data Layer:** SEC EDGAR API + XBRL parsing
- **Analysis:** Custom rule-based + thresholds
- **LLM:** OpenAI gpt-4o-mini

### Key Innovations

1. **Multi-Field XBRL Extraction**  
   Handles companies that change XBRL fields over time (e.g., Apple revenue field change in 2018)

2. **Graceful Degradation**  
   Falls back to rule-based analysis if LLM fails

3. **Zero Configuration**  
   No API keys required (uses free Hugging Face inference)

### File Structure

```
utils/
├── sec_api.py          # SEC EDGAR integration + field mapping
├── red_flag_analyzer.py # Core analysis logic
└── llm_integration.py   # Hugging Face LLM calls
```

---

## Important Disclaimers

This tool is for **transparency and monitoring purposes only**.

**NOT:**
- Financial advice
- Investment recommendations
- Trading signals
- Substitute for professional analysis

**Always:**
- Verify with original SEC filings
- Consult qualified professionals
- Consider multiple data sources

---

## Known Limitations

1. **Ticker Coverage:** Limited to 20 companies (expandable)
2. **XBRL Field Variations:** Some companies use non-standard fields
3. **Model Loading:** First request may timeout (retry works)

---

## Future Enhancements

- Automatic ticker-to-CIK lookup
- Historical trend analysis
- Peer comparison
- PDF report export
- More red flag indicators
- Custom threshold configuration

---

## Resources

- [SEC EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [XBRL US GAAP Taxonomy](https://xbrl.us/home/filers/sec-reporting/)
---

## License

MIT License - Feel free to use and modify

---

## Contributing

Contributions welcome! Areas of interest:
- Additional red flag indicators
- Improved LLM prompts
- UI/UX enhancements
- Bug fixes for edge cases

---

## Contact

For questions or issues, please open a GitHub issue.

---

