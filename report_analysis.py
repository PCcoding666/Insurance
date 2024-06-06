#report_analysis
import logging
import requests
import json
from datetime import datetime
from config import api_key

def analyze_report(report):
    prompt = generate_prompt(report)
    message = {"role": "user", "content": prompt}

    return call_gpt_4o_report(message)

def generate_prompt(report):
    prompt = (
        "The following is the JSON data of a health check report. Please review and identify any abnormalities.\n"
        "Check the health indicators, and if there are abnormalities, please indicate which indicators are abnormal and explain the reasons.\n"
        f"Health check report JSON data:\n{report}\n"
        "Your output should with headings like: '1. Abnormal conditions of health indicators; '\n"
        "For heading , if there are health-related abnormalities, please return the abnormal values and their explanations, formatted as:\n"
        "{'item_name': 'Indicator Name', 'result': 'Test Result', 'reference_range': 'Reference Range', 'remark': 'Remark', 'explanation': 'Explanation'}.\n"
        'If there are comprehensive diagnostic suggestions, print the diagnostic suggestions directly.\n'
        "If some items data are missing, please ignore such items" 
        "If it does not fall into the above two situations, please return: 'No abnormalities found'.\n"
    )
    return prompt

def call_gpt_4o_report(message):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "gpt-4o",
        "messages": [message],
        "temperature": 0.3
    }
    start_time = datetime.now()
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    end_time = datetime.now()
    duration = end_time - start_time
    if response.status_code == 200:
        response_data = response.json()
        structured_data = response_data['choices'][0]['message']['content']
        input_tokens = response_data.get('usage', {}).get('prompt_tokens', 0)
        output_tokens = response_data.get('usage', {}).get('completion_tokens', 0)
        logging.info(f"Response for report analysis: {structured_data}")
        return structured_data, duration.total_seconds(), input_tokens, output_tokens
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None, 0, 0, 0
