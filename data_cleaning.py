# data_cleaning.py
import re

# data_cleaning.py
def clean_response(response):
    # 使用正则表达式提取 {} 中的内容
    match = re.search(r'\{.*\}', response)
    if match:
        extracted_content = match.group(0)  # 获取匹配的内容，包括花括号
        # 去除换行符和多余的空格
        cleaned_content = extracted_content.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
        return cleaned_content
    else:
        return ''  # 如果没有匹配到，返回空字符串