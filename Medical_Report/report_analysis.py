# report_analysis.py

import logging
import requests
import json
from datetime import datetime
from my_config import api_key

def analysis_medical_prompt(report):
    """
    Generate a prompt for analyzing a health check report.

    :param report: The JSON data of the health check report.
    :return: The generated prompt string.
    """
    prompt = (
        "The following is the JSON data of a health check report. Please review and identify any abnormalities.\n"
        "Check the health indicators, and if there are abnormalities, please indicate which indicators are abnormal and explain the reasons.\n"
        f"Health check report JSON data:\n{report}\n"
        "Your output should with headings like: '1. Abnormal conditions of health indicators; 2. Comprehensive diagnostic suggestions'\n"
        "For heading 1, if there are health-related abnormalities, please return the abnormal values and their explanations, formatted as:\n"
        "{'item_name': 'Indicator Name', 'result': 'Test Result', 'reference_range': 'Reference Range', 'remark': 'Remark', 'explanation': 'Explanation'}.\n"
        'If there are comprehensive diagnostic suggestions, print the diagnostic suggestions directly.\n'
        'All content should be in markdown form. \n'
        "If any heading you have no output, for heading 1:please return: 'No abnormalities found'.For heading 2, please return 'diagnostic suggestions'\n"
    )
    return prompt

def analyze_report(report):
    """
    Analyze a health check report using GPT-4o.

    :param report: The JSON data of the health check report.
    :return: Analysis results, duration, input tokens, and output tokens.
    """
    prompt = analysis_medical_prompt(report)
    message = {"role": "user", "content": prompt}
    return call_gpt_4o_report(message)

def call_gpt_4o_report(message):
    """
    Call the GPT-4o API to analyze the report.

    :param message: The message payload for the API call.
    :return: Analysis results, duration, input tokens, and output tokens.
    """
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