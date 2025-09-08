import os
import spacy
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from src.doctor_prompt import doctor_prompt
from src.doctor_mapper import specialist_mapping

# Load environment variables
load_dotenv()

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


# Extract Data from PDF files
def load_pdf_file(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents = loader.load()
    return documents


# Preprocess text using spaCy
def preprocess_text(text):
    doc = nlp(text)
    # Lemmatize, lowercase, remove stopwords & punctuation
    tokens = [
        token.lemma_.lower() for token in doc
        if not token.is_stop and not token.is_punct
    ]
    return " ".join(tokens)


# Split the Data into Text Chunks
def text_split(extracted_data):
    # Apply preprocessing to each document before splitting
    preprocessed_docs = []
    for doc in extracted_data:
        doc.page_content = preprocess_text(doc.page_content)
        preprocessed_docs.append(doc)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(preprocessed_docs)
    return text_chunks


# Download biomedical embeddings from HuggingFace
def download_hugging_face_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
    )
    return embeddings


# Create the chain for doctor recommendation
doctor_prompt_template = ChatPromptTemplate.from_template(doctor_prompt)

# ✅ Fix: explicitly pass API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found. Please check your .env file.")

doctor_llm = OpenAI(
    temperature=0,  # deterministic output
    api_key=openai_api_key
)

doctor_chain = LLMChain(llm=doctor_llm, prompt=doctor_prompt_template)


# AI doctor recommendation function
def get_ai_doctor_recommendation(user_input: str):
    try:
        result = doctor_chain.run({"input": user_input})
        specialty = result.strip()
        return f"\n\nFor your symptoms, you should consult a **{specialty}**."
    except Exception:
        return "\n\nFor your symptoms, you should consult a **General Physician**."
