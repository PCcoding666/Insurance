# config.py
import openai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Your OpenAI API key
api_key = 'sk-proj-5c5PuieVb45JrUQN3FVhT3BlbkFJJJFnKGadNLdWO75xhusD'
openai.api_key = api_key

# Qwen API key
qwen_api_key = 'sk-efa969045c73480c979a6faed83a78a9'

# Azure Document Intelligent
endpoint = "https://validationcomparisonwithgpt4o.cognitiveservices.azure.com/"
key = "6d166f7906c849f886727c9d50e19b40"