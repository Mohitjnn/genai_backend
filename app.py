from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
from langdetect import detect
from deep_translator import GoogleTranslator
import os
from dotenv import load_dotenv
import re

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")


# Configure GenAI API
genai.configure(api_key=api_key)


# Function to extract text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
    return text


# Function to split the extracted text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks


# Function to handle FAISS vector store creation or updating
def get_vector_store(text_chunks, is_new_files=False):
    # Initialize Google Generative AI Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

    if os.path.exists("faiss_index"):
        try:
            # Load the existing vector store
            vector_store = FAISS.load_local(
                "faiss_index",
                embeddings=embeddings,
                allow_dangerous_deserialization=True,
            )

            # If new files are uploaded, add new chunks to the vector store
            if is_new_files and text_chunks:
                vector_store.add_texts(text_chunks, embedding=embeddings)

        except Exception as e:
            raise Exception(f"Error loading or updating FAISS index: {str(e)}")
    else:
        try:
            # Create a new FAISS vector store
            vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
        except Exception as e:
            raise Exception(f"Error creating FAISS index: {str(e)}")

    # Save the FAISS index
    try:
        vector_store.save_local("faiss_index")
    except Exception as e:
        raise Exception(f"Error saving FAISS index: {str(e)}")


# Function to initialize the conversation chain with GenAI
def get_conversational_chain():
    context = """
    You are an AI model designed to assist as a legal consultant knowledgeable about the Constitution of India and the Indian Penal Code. You are provided with one or more PDF files containing legal documents of individuals, along with a legal query related to those documents. Your task is to extract relevant legal information from the provided documents and answer the legal query with accuracy and detail.
    """

    # Define a prompt template to customize the interaction
    prompt_template = """
    ### Inputs:
    - **PDF Legal Document(s)**: {documents}
    - **Query**: {query}

    ### Steps:
    1. **Understand the Query**: Carefully read and comprehend the legal query or issue presented by the user.
    2. **Extract Relevant Information**: Analyze the provided PDFs to identify and extract pertinent information or clauses relevant to the query.
    3. **Identify Relevant Laws**: Determine which sections of the Constitution of India or the Indian Penal Code apply to the query.
    4. **Research or Recall Details**: Use your knowledge or reference materials to gather detailed information about the relevant laws and their interpretations.
    5. **Analyze the Situation**: Consider how the laws and the information from the documents apply to the specific circumstances of the query.
    6. **Provide Clear Advice**: Offer a well-structured and legally sound response or advice, ensuring it addresses all aspects of the query.
    7. **Include Citations**: If applicable, refer to specific articles, sections, or precedents that support the response.

    ### Output Format:
    Provide a detailed and structured paragraph response that includes citations to specific legal provisions when possible.
    Ensure that the advice is legally accurate.
    """

    # Initialize the Google Generative AI model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

    # Create a prompt template that dynamically accepts documents and user queries
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["documents", "query"]
    )

    # Create a question-answering chain using the model
    chain = load_qa_chain(llm=model, chain_type="stuff")

    return chain


def detect_language(text):
    return detect(text)


# Function to translate text into the target language
def translate_text(text, target_language):
    return GoogleTranslator(source="auto", target=target_language).translate(text)


# Modify the `user_input` function to include language detection and translation to English before processing
def user_input(user_question):
    # Detect the language of the query
    query_language = detect_language(user_question)

    # Translate the query to English if it is not already in English
    if query_language != "en":
        print(f"Translating query from {query_language} to English...")
        user_question = translate_text(user_question, "en")

    # Process the query with AI and get the response in English (default)
    ai_response = process_ai_response(user_question)

    # If the query was not originally in English, translate the AI response back to the original language
    if query_language != "en":
        print(f"Translating response back to {query_language}...")
        ai_response = translate_text(ai_response, query_language)

    return ai_response


# Function to handle the AI query processing (same as your original logic)
def process_ai_response(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    try:
        vector_store = FAISS.load_local(
            "faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True
        )
        docs = vector_store.similarity_search(user_question)
    except Exception as e:
        raise Exception(f"Error retrieving similar documents: {str(e)}")

    chain = get_conversational_chain()

    try:
        # Generate response based on the similar documents and user query
        response = chain(
            {
                "input_documents": docs,
                "context": " ".join(doc.page_content for doc in docs),
                "question": user_question,
            },
            return_only_outputs=True,
        )
        return response["output_text"]
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")


# Function to format the response for frontend
def format_response_for_frontend(response):
    # Replace markdown-like bold (**text**) with <strong>text</strong>
    response = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", response)

    # Replace newlines \n with <br/>
    response = response.replace(
        "\n\n", "<br/><br/>"
    )  # For double newlines (paragraph breaks)
    response = response.replace("\n", "<br/>")  # For single newlines (line breaks)

    return response


# Main function to handle the user query, process PDF text, and generate a formatted response
def handle_user_query(query):
    # Example to retrieve existing FAISS index and generate AI response
    ai_response = user_input(query)

    # Format the response for frontend display
    formatted_response = format_response_for_frontend(ai_response)

    return formatted_response
