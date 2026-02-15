import os
from typing import Dict

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")


def generate_analysis_narrative(analysis_results: Dict) -> str:
   
    try:
        from openai import OpenAI
        
        
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
            return "**OpenAI API Key nnot configured!**"
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        company_name = analysis_results['entity_name']
        overall = analysis_results['overall_assessment']
        summary = analysis_results['summary']
        
        findings = []
        for flag_name, result in analysis_results['red_flags'].items():
            if result['status'] == 'OK':
                severity_emoji = '🔴' if result['severity'] == 'RED' else '🟡' if result['severity'] == 'YELLOW' else '🟢'
                findings.append(f"{severity_emoji} {result['message']}")
        
        findings_text = "\n".join(findings)
        
        prompt = f"""You are a financial analyst explaining accounting stress signals to non-experts.

Company: {company_name}
Overall Signal: {overall}
Red Flags: {summary['red_flags_count']} | Yellow: {summary['yellow_flags_count']} | Green: {summary['green_flags_count']}

Findings:
{findings_text}

Task: Write a brief 3-4 sentence analysis in clear language. Do NOT use asterisks or bold formatting. Do not mention the color of the signal
Include the following points, each in one new paragraph:
1. Main takeaway (is this company showing stress?)
2. If there are multiple concerning signals, list them as bullet points using the • symbol, each bullet should be in a new line
3. What potential investors should monitor

Keep it concise and accessible. This is NOT investment advice - it's a transparency tool."""

        print("\n Calling OpenAI API...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a financial transparency analyst helping non-experts understand company filings."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        text = response.choices[0].message.content.strip()
        
              
        return text
        
    except ImportError:
        return "**OpenAI library not installed!**\n\nRun in terminal:\n```\npip install openai\n```"
    
    except Exception as e:
        error_msg = str(e)
        
        # Mensagens de erro amigáveis
        if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
            return f"**Invalid API Key**\n\nYour OpenAI API key appears to be invalid. Please check:\n1. Go to https://platform.openai.com/api-keys\n2. Create a new key\n3. Copy and paste it in `utils/llm_integration_openai.py` line 18"
        
        elif "insufficient_quota" in error_msg.lower():
            return f"**Insufficient Credits**\n\nYou need to add credits to your OpenAI account:\n1. Go to https://platform.openai.com/account/billing\n2. Add at least $5\n3. Try again"
        
        else:
            return f"**OpenAI API Error**\n\n{error_msg}\n\nPlease check:\n- Your internet connection\n- Your API key is valid\n- You have credits in your account"


def test_openai():
    
    print("🧪 Testing OpenAI API...\n")
    
    if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-...":
        print("API key not configured!")
        return False
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        print("Sending test message...")
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'Hello! OpenAI is working!'"}],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        
        print(f"\nOpenAI working!")
        return True
        
    except ImportError:
        print("Biblioteca OpenAI not installed!")
        return False
        
    except Exception as e:
        print(f"Error: {e}\n")
        
        if "authentication" in str(e).lower():
            print("API key invalid.")
        elif "insufficient_quota" in str(e).lower():
            print("No credits.")
        
        return False


if __name__ == "__main__":
    test_openai()
