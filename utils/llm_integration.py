

import requests
import time
from typing import Dict, Optional
from config import HF_API_URL, HF_MAX_TOKENS, HF_TEMPERATURE


def generate_analysis_narrative(analysis_results: Dict, use_fallback: bool = False) -> str:
    
    prompt = build_analysis_prompt(analysis_results)
    
    
    try:
        narrative = query_huggingface(prompt)
        
        if narrative:
            print("="*70)
            print("LLM connected!")
            print("="*70 + "\n")
            return narrative
        else:
            print("="*70)
            print("LLM not connected")
            print("="*70 + "\n")
            
            if use_fallback:
                print("Using fallback")
                return generate_rule_based_analysis(analysis_results)
            else:
                return "⚠️ **LLM Error:** The AI model did not respond after multiple attempts. This may be due to high demand on the free Hugging Face API. Please try again in a few moments, or enable fallback mode in the code."
            
    except Exception as e:
        print(f"="*70)
        print(f"ERROR: {e}")
        print("="*70 + "\n")
        
        if use_fallback:
            return generate_rule_based_analysis(analysis_results)
        else:
            return f"**Critical Error:** {str(e)}"


def build_analysis_prompt(analysis_results: Dict) -> str:

    company_name = analysis_results['entity_name']
    overall = analysis_results['overall_assessment']
    summary = analysis_results['summary']
    
    findings = []
    for flag_name, result in analysis_results['red_flags'].items():
        if result['status'] == 'OK':
            severity_emoji = '🔴' if result['severity'] == 'RED' else '🟡' if result['severity'] == 'YELLOW' else '🟢'
            findings.append(f"{severity_emoji} {result['message']}")
    
    findings_text = "\n".join(findings)
    
    prompt = f"""<s>[INST] You are a financial analyst explaining accounting stress signals to non-experts.

Company: {company_name}
Overall Signal: {overall}
Red Flags: {summary['red_flags_count']} | Yellow: {summary['yellow_flags_count']} | Green: {summary['green_flags_count']}

Findings:
{findings_text}

Task: Write a brief 3-4 sentence analysis in clear language. Focus on:
1. Main takeaway (is this company showing stress?)
2. Most concerning signal (if any)
3. What stakeholders should monitor

Keep it concise and accessible. This is NOT investment advice - it's a transparency tool.
[/INST]"""
    
    return prompt


def query_huggingface(prompt: str, max_retries: int = 3) -> Optional[str]:

    try:
        from huggingface_hub import InferenceClient
        
        # Criar cliente com seu token
        client = InferenceClient(
            token="HF_TOKEN"
        )
        
        
        # Chamar modelo
        response = client.chat_completion(
            prompt,
            model="zai-org/GLM-4.5",
            max_tokens=500,
            temperature=0.7,
        )
        
        if response:
            print(f" LLM connected! Size: {len(response)} char")
            return response.strip()
        else:
            print("Answer empty")
            return None
            
    except ImportError:
        print("huggingface_hub not installed!")
        return None
        
    except Exception as e:
        print(f"Error on HF: {e}")
        return None


def generate_rule_based_analysis(analysis_results: Dict) -> str:

    company_name = analysis_results['entity_name']
    overall = analysis_results['overall_assessment']
    summary = analysis_results['summary']
    red_flags = analysis_results['red_flags']
    
    critical_flags = [
        name for name, result in red_flags.items()
        if result.get('severity') == 'RED'
    ]
    
    warning_flags = [
        name for name, result in red_flags.items()
        if result.get('severity') == 'YELLOW'
    ]
    
    if overall == 'RED':
        intro = f"{company_name} shows significant signs of financial stress "
        intro += f"with {summary['red_flags_count']} critical indicators."
    elif overall == 'YELLOW':
        intro = f"{company_name} displays some warning signs "
        intro += f"that warrant close monitoring."
    else:
        intro = f"{company_name} presents healthy financial indicators "
        intro += f"with no critical stress signals."
    
    if critical_flags:
        concern_messages = []
        for flag in critical_flags:
            result = red_flags[flag]
            concern_messages.append(result['message'])
        
        if len(concern_messages) == 1:
            concerns = f"Key area of concern: {concern_messages[0]}."
        else:
            concerns = "Key areas of concern:\n" + "\n".join([f"• {msg}" for msg in concern_messages])
    elif warning_flags:
        concern_messages = []
        for flag in warning_flags[:2]:  
            result = red_flags[flag]
            concern_messages.append(result['message'])
        
        if len(concern_messages) == 1:
            concerns = f"Area to monitor: {concern_messages[0]}."
        else:
            concerns = "Areas to monitor:\n" + "\n".join([f"• {msg}" for msg in concern_messages])
    else:
        concerns = "The company demonstrates stability across key financial metrics."
    
    if overall == 'RED':
        recommendation = "Stakeholders should review the original filings and consider professional in-depth analysis."
    elif overall == 'YELLOW':
        recommendation = "We recommend monitoring the next quarterly reports to verify trends."
    else:
        recommendation = "Continue monitoring through regular filings to identify early changes."
    
    return f"{intro}\n\n{concerns}\n\n{recommendation}"
