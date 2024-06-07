# config.py
import openai
import logging
import os
import streamlit as st

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Your OpenAI API key
api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = api_key

# Qwen API key
qwen_api_key = 'sk-efa969045c73480c979a6faed83a78a9'

# Azure Document Intelligent
endpoint = "https://validationcomparisonwithgpt4o.cognitiveservices.azure.com/"
key = "6d166f7906c849f886727c9d50e19b40"
