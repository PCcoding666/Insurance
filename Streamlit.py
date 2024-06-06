import os
import json
import logging
import streamlit as st
import re
import pandas as pd
from api_calls import get_structured_data_from_image
from batch_processing import process_images_and_merge
from pdf_to_images import pdf_to_images
from report_analysis import analyze_report

logging.basicConfig(level=logging.INFO)

def process_file(files, model="gpt-4o"):
    custom_prompt = """
        Please extract the results in this image and turn them into structured data in JSON format. 
        Pay special attention to horizontal alignment when extracting text, there may have some skip part in one row of datalike '参考区间'. 
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
        json_parts, suggestions = extract_json_and_suggestions(analysis_result)
        json_analysis_result = json.dumps(json_parts, ensure_ascii=False, indent=2)
        return json_analysis_result, suggestions, duration, input_tokens, output_tokens
    except Exception as e:
        logging.error(f"Error analyzing report: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2), "", 0, 0, 0

def extract_json_and_suggestions(response):
    # Extract all JSON parts from the response and the suggestions part
    json_parts = []
    suggestions = ""
    
    # Extract JSON parts
    matches = re.findall(r'\{.*?\}', response, re.DOTALL)
    for match in matches:
        try:
            json_parts.append(json.loads(match))
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing part as JSON: {e}")
            continue
    
    # Extract suggestions part
    suggestions_match = re.search(r'Comprehensive diagnostic suggestions:(.*)', response, re.DOTALL)
    if suggestions_match:
        suggestions = suggestions_match.group(1).strip()
    
    return json_parts, suggestions

def clean_response(response):
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        extracted_content = match.group(0)
        cleaned_content = extracted_content.replace('\n', ' ').replace('\r', ' ').replace('  ', ' ')
        try:
            return json.loads(cleaned_content)
        except json.JSONDecodeError:
            return cleaned_content
    else:
        return response

def json_to_dataframe(json_data, keys):
    data = []
    for item in json_data:
        row = {key: item.get(key, None) for key in keys}
        data.append(row)
    return pd.DataFrame(data)

def main():
    st.title("Medical report")

    if 'metadata' not in st.session_state:
        st.session_state.metadata = ""
    if 'submit_result' not in st.session_state:
        st.session_state.submit_result = ""

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
                
                # Display results in table format
                keys = ["No", "项目", "结果", "单位", "参考区间"]
                for filename, json_data in parsed_result.items():
                    if isinstance(json_data, dict) and "results" in json_data:
                        df = json_to_dataframe(json_data["results"], keys)
                        st.markdown(f"#### Results for {filename}")
                        st.dataframe(df)
                
                st.text(f"Processing Time 1: {duration}")
        else:
            st.warning("Please upload at least one file.")

    if st.button("Risk Assessment"):
        metadata = st.session_state.metadata
        if metadata:
            with st.spinner('Analyzing...'):
                result, suggestions, duration, input_tokens, output_tokens = run_analysis(metadata)
                try:
                    parsed_result = json.loads(result)
                    result_str = json.dumps(parsed_result, ensure_ascii=False, indent=2)
                except json.JSONDecodeError:
                    result_str = result
                st.markdown(st.session_state.submit_result)  # Display the Submit result again
                st.markdown(f"### Risk Assessment Report\n```json\n{result_str}\n```")
                
                # Display analysis results in table format
                keys = ["item_name", "result", "reference_range", "remark", "explanation"]
                df = json_to_dataframe(parsed_result, keys)
                st.dataframe(df)
                
                if suggestions:
                    st.markdown(f"### Comprehensive Diagnostic Suggestions\n{suggestions}")
                st.text(f"Processing Time 2: {duration}")
        else:
            st.warning("Please provide metadata for analysis.")

if __name__ == "__main__":
    main()
