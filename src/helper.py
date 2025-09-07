from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings   # updated import

# import the correct mapping
from src.doctor_mapper import specialist_mapping


# Extract Data from the PDF file
def load_pdf_file(data):
    loader = DirectoryLoader(data,
                             glob="*.pdf",
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents


# Split the Data into Text Chunks
def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks


# Download the embeddings from HuggingFace
def download_hugging_face_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    return embeddings   # ✅ FIXED


# Doctor recommendation function
def get_doctor_recommendation(user_input: str):
    user_input = user_input.lower()
    for symptom, doctor in specialist_mapping.items():   # ✅ FIXED
        if symptom in user_input:
            return f"\n\n  For your symptoms ({symptom}), you should consult a **{doctor}**."
    return None
