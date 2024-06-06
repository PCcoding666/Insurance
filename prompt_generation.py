# prompt_generation.py
def generate_prompt(report):
    prompt = (
        "The following is the JSON data of a health check report. Please review and identify any abnormalities.\n"
        "1. Check the health indicators, and if there are abnormalities, please indicate which indicators are abnormal and explain the reasons.\n"
        "2. Display some attribute information contained in the report, such as date, total amount, location, etc.\n"
        "If no relevant information is found, please return 'No relevant information found'.\n"
        f"Health check report JSON data:\n{report}\n"
        "Your output should include two aspects, displayed with two headings: '1. Abnormal conditions of health indicators; 2. Insurance information disclosure'\n"
        "For heading 1, if there are health-related abnormalities, please return the abnormal values and their explanations, formatted as: {'item_name': 'Indicator Name', 'result': 'Test Result', 'reference_range': 'Reference Range', 'remark': 'Remark', 'explanation': 'Explanation'}.\n"
        'If there are comprehensive diagnostic suggestions, print the diagnostic suggestions directly.\n'
        "If it does not fall into the above two situations, please return: 'No abnormalities found'.\n"
        "For heading 2, please display all information that may relate to insurance claims, including the time, place, invoice details, and expenses covered in the report, etc. Use JSON format to display, and if there is no relevant information, output N.A.\n"
        "Do not use omissions expression"
    )
    return prompt
