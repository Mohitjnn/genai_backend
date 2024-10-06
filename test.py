from typing import Optional
import os

# Import necessary functions from the GenAI logic
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader
from app import (
    get_pdf_text,
    get_text_chunks,
    get_vector_store,
    user_input,
    format_response_for_frontend,
)

# Define default legal documents
DEFAULT_DOCS = [
    "indian-penal-code.pdf",
    "20240716890312078.pdf",
]  # Replace with actual file paths if necessary


def process_file_and_text(file: Optional[bytes], file_name: str, text: str):
    # If a file is provided, process the file
    if file:
        # Save the file locally
        file_path = f"./{file_name}"
        with open(file_path, "wb") as f:
            f.write(file)

        # Extract text from the uploaded PDF
        pdf_docs = [file_path]
        pdf_text = get_pdf_text(pdf_docs)
        text_chunks = get_text_chunks(pdf_text)

        # Update or create the FAISS vector store
        get_vector_store(text_chunks, is_new_files=True)

        # Return result if a text query is provided
        if text:
            # Get the AI response
            ai_response = user_input(text)

            # Format the response for the frontend
            formatted_response = format_response_for_frontend(ai_response)
            return formatted_response
        else:
            return "File uploaded and processed successfully. No query provided."

    # If only text is provided, process the text using existing documents
    elif text:
        if not os.path.exists("faiss_index"):
            # Process the default legal documents if no FAISS index exists
            pdf_text = get_pdf_text(DEFAULT_DOCS)
            text_chunks = get_text_chunks(pdf_text)
            get_vector_store(text_chunks, is_new_files=False)

        # Handle text query
        ai_response = user_input(text)

        # Format the response for the frontend
        formatted_response = format_response_for_frontend(ai_response)
        return formatted_response

    return "No file or text provided."
