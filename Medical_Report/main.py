import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import logging
import streamlit as st
from api_calls import get_structured_data_from_image
from batch_processing import process_images_and_merge
from report_analysis import analyze_report
from my_utils import pdf_to_images, clean_response



logging.basicConfig(level=logging.INFO)

def process_file(files, model="gpt-4o"):
    custom_prompt = """
        Please extract the results in this image and turn them into structured data in JSON format. 
        Pay special attention to horizontal alignment when extracting text, there may have some skip part in one row of data like '参考区间'. 
        When processing data in a table, grab the data row by row. 
        For content where some information in the image is blocked or unclear, use Not Visible as the output. Output content don't need to translate, keep it original. 
        Your output does not need to contain any additional information.
    """
    results = {}
    total_duration = 0
    total_input_tokens = 0
    total_output_tokens = 0
    for file in files:
        file_name = file.name
        file_bytes = file.read()
        if file_name.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(file_bytes, custom_prompt, model)
            results[file_name] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        elif file_name.lower().endswith('pdf'):
            output_folder = 'extracted_images'
            os.makedirs(output_folder, exist_ok=True)
            pdf_path = os.path.join(output_folder, file_name)
            with open(pdf_path, 'wb') as f:
                f.write(file_bytes)
            image_paths = pdf_to_images(pdf_path, output_folder, dpi=300)
            structured_data, duration, input_tokens, output_tokens = process_images_and_merge(image_paths, custom_prompt, model)
            results[file_name] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        else:
            results[file_name] = {"error": "Unsupported file type"}

    return results, total_duration, total_input_tokens, total_output_tokens

def get_metadata(files):
    try:
        results, duration, input_tokens, output_tokens = process_file(files)
        cleaned_results = {k: clean_response(v) if isinstance(v, str) else v for k, v in results.items()}
        json_results = json.dumps(cleaned_results, ensure_ascii=False, indent=2)
        return json_results, duration, input_tokens, output_tokens
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2), 0, 0, 0

def run_analysis(metadata):
    logging.info(f"Metadata: {metadata}")
    metadata = metadata.strip().strip('```json').strip('```')
    try:
        analysis_result, duration, input_tokens, output_tokens = analyze_report(metadata)
        logging.info(f"Analysis result: {analysis_result}")
        return analysis_result, duration, input_tokens, output_tokens
    except Exception as e:
        logging.error(f"Error analyzing report: {str(e)}")
        return str(e), 0, 0, 0

def format_markdown(analysis_result):
    try:
        analysis_data = json.loads(analysis_result)
        abnormal_conditions = analysis_data.get("abnormal_conditions", [])
        suggestions = analysis_data.get("suggestions", [])
        
        md = "# 1. Abnormal conditions of health indicators\n\n"
        for idx, condition in enumerate(abnormal_conditions, 1):
            md += f"**{idx}.** 项目: {condition['item_name']}\n"
            md += f"   - 结果: {condition['result']}\n"
            md += f"   - 参考区间: {condition['reference_range']}\n"
            md += f"   - 备注: {condition['remark']}\n"
            md += f"   - 解释: {condition['explanation']}\n\n"

        md += "# 2. Comprehensive diagnostic suggestions\n\n"
        for suggestion in suggestions:
            md += f"- {suggestion}\n"
        
        return md
    except Exception as e:
        logging.error(f"Error formatting markdown: {str(e)}")
        return analysis_result

def main():
    st.title("Medical Report Processing")

    if 'metadata' not in st.session_state:
        st.session_state.metadata = ""
    if 'submit_result' not in st.session_state:
        st.session_state.submit_result = ""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = ""

    uploaded_files = st.file_uploader("Upload Image(s) or PDF", type=["png", "jpg", "jpeg", "bmp", "gif", "pdf"], accept_multiple_files=True)

    if st.button("Submit"):
        if uploaded_files:
            with st.spinner('Processing...'):
                result, duration, input_tokens, output_tokens = get_metadata(uploaded_files)
                try:
                    parsed_result = json.loads(result)
                    result_str = json.dumps(parsed_result, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    result_str = result
                st.session_state.metadata = result_str
                st.session_state.submit_result = f"### Metadata\n```json\n{result_str}\n```"
                st.markdown(st.session_state.submit_result)
                st.text(f"Processing Time: {duration}")
        else:
            st.warning("Please upload at least one file.")

    if st.button("Risk Assessment"):
        metadata = st.session_state.metadata
        if metadata:
            with st.spinner('Analyzing...'):
                result, duration, input_tokens, output_tokens = run_analysis(metadata)
                formatted_result = format_markdown(result)
                st.session_state.analysis_result = formatted_result
                st.markdown(f"### Risk Assessment Report\n{formatted_result}")
                st.text(f"Processing Time: {duration}")
        else:
            st.warning("Please provide metadata for analysis.")

if __name__ == "__main__":
    main()
