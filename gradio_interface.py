# gradio_interface.py
import os
import json
import logging
import gradio as gr
from api_calls import get_structured_data_from_image
from batch_processing import process_images_and_merge
from pdf_to_images import pdf_to_images
from report_analysis import analyze_report

def process_file(files, model):
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
        file_path = file.name
        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(file_path, custom_prompt, model)
            results[file_path] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        elif file_path.lower().endswith('pdf'):
            output_folder = 'extracted_images'
            os.makedirs(output_folder, exist_ok=True)
            image_paths = pdf_to_images(file_path, output_folder, dpi=300)
            structured_data, duration, input_tokens, output_tokens = process_images_and_merge(image_paths, custom_prompt, model)
            results[file_path] = structured_data
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        else:
            results[file_path] = {"error": "Unsupported file type"}

    json_results = json.dumps(results, ensure_ascii=False, indent=2)
    json_results = json_results.replace('\\n', '\n')
    return json_results, total_duration, total_input_tokens, total_output_tokens

def get_metadata(files, model):
    results, duration, input_tokens, output_tokens = process_file(files, model)
    return results, duration, input_tokens, output_tokens

def run_analysis(metadata):
    logging.info(f"Metadata: {metadata}")
    metadata = metadata.strip().strip('```json').strip('```')
    analysis_result, duration, input_tokens, output_tokens = analyze_report(metadata)
    return analysis_result, duration, input_tokens, output_tokens

def create_interface():
    with gr.Blocks() as demo:
        with gr.Column():
            file_input = gr.File(label="Upload Image(s) or PDF", type="file", file_count="multiple")
            with gr.Row():
                model_choice = gr.Dropdown(label="Choose Model", choices=["gpt-4o", "qwen-vl-max"], value="gpt-4o")
                submit_button = gr.Button("Submit", size="small")
            metadata_output = gr.Textbox(label="Metadata", lines=10)
            with gr.Row():
                processing_time_output_1 = gr.Textbox(label="Processing Time 1", lines=1)
                input_tokens_output_1 = gr.Textbox(label="Input Tokens 1", lines=1)
                output_tokens_output_1 = gr.Textbox(label="Output Tokens 1", lines=1)
            risk_button = gr.Button("Risk Assessment")
            risk_output = gr.Textbox(label="Risk Assessment Report", lines=10)
            with gr.Row():
                processing_time_output_2 = gr.Textbox(label="Processing Time 2", lines=1)
                input_tokens_output_2 = gr.Textbox(label="Input Tokens 2", lines=1)
                output_tokens_output_2 = gr.Textbox(label="Output Tokens 2", lines=1)

        submit_button.click(fn=lambda files, model: get_metadata(files, model), inputs=[file_input, model_choice], outputs=[metadata_output, processing_time_output_1, input_tokens_output_1, output_tokens_output_1])
        risk_button.click(fn=lambda metadata: run_analysis(metadata), inputs=[metadata_output], outputs=[risk_output, processing_time_output_2, input_tokens_output_2, output_tokens_output_2])

    return demo
