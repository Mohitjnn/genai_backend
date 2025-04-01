import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

from typing import Optional
from app import get_pdf_text, get_text_chunks

# Fix for duplicate library loading
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Define paths
BASE_DIR = os.path.abspath("artifacts")
TOKENIZER_PATH = os.path.join(BASE_DIR, "tokenizer")
MODEL_PATH = os.path.join(BASE_DIR, "pegasus-samsum-model")

# Check if CUDA (GPU) is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load tokenizer and model with error handling
try:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, local_files_only=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH, local_files_only=True)
except Exception as e:
    print(f"❌ Error loading model/tokenizer: {e}")
    tokenizer, model = None, None  # Prevents crashes if the model is missing

def getPdfSummary(file: Optional[bytes], file_name: str) -> str:
    if file:
        # Save the file locally
        file_path = f"./{file_name}"
        with open(file_path, "wb") as f:
            f.write(file)

        # Extract text from the uploaded PDF
        pdf_docs = [file_path]
        pdf_text = get_pdf_text(pdf_docs)
        # print(pdf_text)
        
        summary = getSummary(pdf_text)
        
        os.remove(file_path)  
        
        return summary
    return ""

# Summarization function
def getSummary(text: str) -> str:
    if tokenizer is None or model is None:
        return "Model not loaded properly!"

    # Lazy load pipeline (avoids unnecessary GPU memory usage)
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=0 if DEVICE == "cuda" else -1)
    
    # Generate summary with optimized parameters
    gen_kwargs = {"length_penalty": 0.8, "num_beams": 8, "max_length": 128}
    summary = summarizer(text, **gen_kwargs)
    
    return summary[0]["summary_text"] if summary else "No summary generated."
