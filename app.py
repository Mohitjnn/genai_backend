from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure GenAI API
import google.generativeai as genai

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
    You are an AI model designed to assist as a legal consultant knowledgeable about the Constitution of India and the Indian Penal Code. 
    You are provided with PDF files containing legal documents, along with a query related to those documents. Your task is to 
    extract relevant legal information from the provided documents and answer the query with accuracy.
    """

    # Define a prompt template to customize the interaction
    prompt_template = """
    ### Inputs:
    - **PDF Legal Document(s)**: {documents}
    - **Query**: {query}

    ### Output Format:
    Provide a detailed and structured paragraph response, citing specific legal provisions when necessary.
    """

    # Initialize the Google Generative AI model
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)

    # Create a question-answering chain using the model
    chain = load_qa_chain(llm=model, chain_type="stuff")

    return chain


# Function to handle user query and return AI-generated response
def user_input(user_question):
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
