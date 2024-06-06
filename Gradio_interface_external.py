import os
import json
import logging
import gradio as gr
from api_calls import get_structured_data_from_image
from batch_processing import process_images_and_merge
from pdf_to_images import pdf_to_images
from report_analysis import analyze_report

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
        file_path = file.name
        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(file_data, custom_prompt, model)
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

    return results, total_duration, total_input_tokens, total_output_tokens

def get_metadata(files):
    try:
        results, duration, input_tokens, output_tokens = process_file(files)
        json_results = json.dumps(results, ensure_ascii=False, indent=2)
        return json_results, duration, input_tokens, output_tokens
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2), 0, 0, 0

def run_analysis(metadata):
    logging.info(f"Metadata: {metadata}")
    metadata = metadata.strip().strip('```json').strip('```')
    try:
        analysis_result, duration, input_tokens, output_tokens = analyze_report(metadata)
        json_analysis_result = json.dumps(analysis_result, ensure_ascii=False, indent=2)
        return json_analysis_result, duration, input_tokens, output_tokens
    except Exception as e:
        logging.error(f"Error analyzing report: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2), 0, 0, 0

def create_interface():
    with gr.Blocks() as demo:
        with gr.Column():
            file_input = gr.File(label="Upload Image(s) or PDF", type="file", file_count="multiple")
            submit_button = gr.Button("Submit", size="small")
            metadata_output = gr.Markdown(label="Metadata")
            with gr.Row():
                processing_time_output_1 = gr.Textbox(label="Processing Time 1", lines=1)
            risk_button = gr.Button("Risk Assessment")
            risk_output = gr.Markdown(label="Risk Assessment Report")
            with gr.Row():
                processing_time_output_2 = gr.Textbox(label="Processing Time 2", lines=1)

        def submit_click(files):
            result, duration, input_tokens, output_tokens = get_metadata(files)
            return f"```json\n{result}\n```", duration

        def risk_assessment_click(metadata):
            result, duration, input_tokens, output_tokens = run_analysis(metadata)
            return f"```json\n{result}\n```", duration

        submit_button.click(fn=submit_click, inputs=[file_input], outputs=[metadata_output, processing_time_output_1])
        risk_button.click(fn=risk_assessment_click, inputs=[metadata_output], outputs=[risk_output, processing_time_output_2])

    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)
