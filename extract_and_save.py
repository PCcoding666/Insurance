import os
import json
import pandas as pd
import streamlit as st
from api_calls import get_structured_data_from_image
from batch_processing import process_images_and_merge
from pdf_to_images import pdf_to_images

def process_file(files, model, output_csv_path):
    custom_prompt = """
        Please extract the results in this image and turn them into structured data in JSON format. 
        Pay special attention to horizontal alignment when extracting text, there may have some skip part in one row of data like '参考区间'. 
        For content where some information in the image is blocked or unclear, use Not Visible as the output. Output content don't need to translate, keep it original. 
        Your output does not need to contain any additional information.
    """
    results = []
    total_duration = 0
    total_input_tokens = 0
    total_output_tokens = 0
    
    for file in files:
        file_path = file.name
        file_bytes = file.read()
        if file_path.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
            structured_data, duration, input_tokens, output_tokens = get_structured_data_from_image(file_bytes, custom_prompt, model)
            results.append(structured_data)
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        elif file_path.lower().endswith('pdf'):
            output_folder = 'extracted_images'
            os.makedirs(output_folder, exist_ok=True)
            pdf_path = os.path.join(output_folder, file_path)
            with open(pdf_path, 'wb') as f:
                f.write(file_bytes)
            image_paths = pdf_to_images(pdf_path, output_folder, dpi=300)
            structured_data, duration, input_tokens, output_tokens = process_images_and_merge(image_paths, custom_prompt, model)
            results.append(structured_data)
            total_duration += duration
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
        else:
            results.append({"error": "Unsupported file type"})
    
    df = pd.DataFrame(results)
    df.to_csv(output_csv_path, index=False, encoding='utf-8')
    return df, total_duration, total_input_tokens, total_output_tokens

st.title("Structured Data Extraction")

uploaded_files = st.file_uploader("Upload Image(s) or PDF", type=["png", "jpg", "jpeg", "bmp", "gif", "pdf"], accept_multiple_files=True)
model_choice = st.selectbox("Choose Model", ["gpt-4o", "qwen-vl-max"])

if st.button("Extract and Save"):
    output_csv_path = "/home/ec2-user/Myproject/Insurance/Data/structured_data.csv"
    if uploaded_files:
        df, duration, input_tokens, output_tokens = process_file(uploaded_files, model_choice, output_csv_path)
        st.write(f"Data saved to {output_csv_path}")
        st.dataframe(df)
        st.write(f"Processing Time: {duration} seconds")
        # st.write(f"Input Tokens: {input_tokens}")
        # st.write(f"Output Tokens: {output_tokens}")
    else:
        st.write("Please upload at least one file.")
