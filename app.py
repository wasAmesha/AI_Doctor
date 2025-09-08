from flask import Flask, render_template, jsonify, request
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from src.helper import download_hugging_face_embeddings, get_doctor_recommendation

app = Flask(__name__)

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
# HF_TOKEN = os.environ.get('HF_TOKEN')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
# os.environ["HF_TOKEN"] = HF_TOKEN


embeddings = download_hugging_face_embeddings()

index_name = 'medicalbot'

# Embed each chunk and upsert the embeddings into pinecone index
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)

retriever = docsearch.as_retriever(search_type="similarity",search_kwargs={"k":3})

llm = OpenAI(temperature=0.4, max_tokens=500)
# llm = ChatOpenAI(
#     model="Intelligent-Internet/II-Medical-8B-1706:featherless-ai",
#     temperature=0.4,
#     max_tokens=500,
#     api_key=HF_TOKEN,
#     base_url="https://router.huggingface.co/v1"
# )

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "Question: {input}\n\nContext: {context}")
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)


@app.route("/")
def index():
    return render_template('chat.html')


# @app.route("/get", methods=["GET", "POST"])
# def chat():
#     msg = request.form["msg"]
#     input = msg
#     print(input)
#     response = rag_chain.invoke({"input": msg})
#     print("Response : ", response["answer"])
#     return str(response["answer"])


@app.route("/get", methods=["GET", "POST"])
def chat_with_doctor():
    msg = request.form["msg"]
    print("User:", msg)

    # Step 1: Get AI answer
    response = rag_chain.invoke({"input": msg})
    ai_answer = response["answer"]

    # Step 2: Doctor recommendation
    doctor_suggestion = get_doctor_recommendation(msg)

    if doctor_suggestion:
        final_answer = ai_answer + "\n\n" + doctor_suggestion + \
                       "\n You can channel this specialist via eChannelling or Doc990."
    else:
        final_answer = ai_answer

    print("Response:", final_answer)
    return str(final_answer)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)