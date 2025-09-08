from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from src.helper import download_hugging_face_embeddings, get_ai_doctor_recommendation
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from src.prompt import *
import os
import hashlib
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# -------------------- Flask App --------------------
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# -------------------- Load Environment --------------------
load_dotenv()

# Set API keys for libraries
pinecone_key = os.getenv("PINECONE_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")
if pinecone_key:
    os.environ["PINECONE_API_KEY"] = pinecone_key
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key

# -------------------- MongoDB Setup --------------------
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME', 'medicalbot')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    users_collection = db['users']
    chat_sessions_collection = db['chat_sessions']
    messages_collection = db['messages']
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    users_collection = None

# -------------------- Utility Functions --------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_local_time():
    return datetime.now()

# -------------------- Embeddings & RAG Setup --------------------
embeddings = download_hugging_face_embeddings()
index_name = 'medicalbot'

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings,
)

retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

llm = OpenAI(temperature=0.4, max_tokens=500)

prompt = ChatPromptTemplate.from_template("""
You are a helpful AI doctor assistant.
Use the following context to answer the user's question.
If the context is not relevant, just say you don’t know.

Context:
{context}

Question:
{input}

Answer:
""")

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# -------------------- Routes --------------------
@app.route("/")
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        user = users_collection.find_one({"_id": ObjectId(user_id)})

        chat_sessions = list(chat_sessions_collection.find(
            {"user_id": user_id}
        ).sort("last_activity", -1))

        current_session_id = session.get('current_session_id')
        if not current_session_id:
            new_session = {
                "user_id": user_id,
                "title": "New Chat",
                "created_at": get_local_time(),
                "last_activity": get_local_time(),
                "message_count": 0
            }
            result = chat_sessions_collection.insert_one(new_session)
            current_session_id = str(result.inserted_id)
            session['current_session_id'] = current_session_id

        messages = list(messages_collection.find(
            {"session_id": current_session_id}
        ).sort("timestamp", 1))

        return render_template('chat.html',
                               user_email=user.get('email', ''),
                               chat_sessions=chat_sessions,
                               current_session_id=current_session_id,
                               messages=messages)
    else:
        return redirect(url_for('login'))

@app.route("/session/<session_id>")
def switch_session(session_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    session_obj = chat_sessions_collection.find_one({
        "_id": ObjectId(session_id),
        "user_id": session['user_id']
    })

    if session_obj:
        session['current_session_id'] = session_id
        flash('Switched to selected chat session', 'info')
    else:
        flash('Invalid chat session', 'error')

    return redirect(url_for('index'))

@app.route("/session/new")
def new_session():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    new_session = {
        "user_id": session['user_id'],
        "title": "New Chat",
        "created_at": get_local_time(),
        "last_activity": get_local_time(),
        "message_count": 0
    }
    result = chat_sessions_collection.insert_one(new_session)
    session['current_session_id'] = str(result.inserted_id)

    flash('Started a new chat session', 'info')
    return redirect(url_for('index'))

@app.route("/session/delete/<session_id>", methods=["GET", "POST"])
def delete_session(session_id):
    if 'user_id' not in session:
        if request.method == 'POST':
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        return redirect(url_for('login'))

    try:
        session_obj = chat_sessions_collection.find_one({
            "_id": ObjectId(session_id),
            "user_id": session['user_id']
        })

        if session_obj:
            chat_sessions_collection.delete_one({"_id": ObjectId(session_id)})
            messages_collection.delete_many({"session_id": session_id})

            if session.get('current_session_id') == session_id:
                session.pop('current_session_id', None)

            if request.method == 'POST':
                return jsonify({"success": True, "message": "Chat session deleted"})
            else:
                flash('Chat session deleted', 'info')
                return redirect(url_for('index'))
        else:
            if request.method == 'POST':
                return jsonify({"success": False, "error": "Invalid chat session"}), 404
            else:
                flash('Invalid chat session', 'error')
                return redirect(url_for('index'))

    except Exception as e:
        if request.method == 'POST':
            return jsonify({"success": False, "error": str(e)}), 500
        else:
            flash('Error deleting session: ' + str(e), 'error')
            return redirect(url_for('index'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = hash_password(password)

        if users_collection is not None:
            user = users_collection.find_one({
                "username": username,
                "password": hashed_password
            })

            if user:
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session.pop('current_session_id', None)
                users_collection.update_one(
                    {"_id": user['_id']},
                    {"$set": {"last_login": get_local_time()}}
                )
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error="Invalid credentials")
        else:
            return render_template('login.html', error="Database not available")

    return render_template('login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form.get("email", "")
        hashed_password = hash_password(password)

        if users_collection is not None:
            if users_collection.find_one({"username": username}):
                return render_template('signup.html', error="Username already exists")

            new_user = {
                "username": username,
                "password": hashed_password,
                "email": email,
                "created_at": get_local_time(),
                "last_login": None
            }

            users_collection.insert_one(new_user)
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            return render_template('signup.html', error="Database not available")

    return render_template('signup.html')

@app.route("/logout")
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route("/get", methods=["POST"])
def chat():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401

    current_session_id = session.get('current_session_id')
    if not current_session_id:
        return jsonify({"error": "No active session"}), 400

    msg = request.form["msg"]
    print("User:", msg)

    user_message = {
        "session_id": current_session_id,
        "user_id": session['user_id'],
        "content": msg,
        "sender": "user",
        "timestamp": get_local_time()
    }
    messages_collection.insert_one(user_message)

    # -------------------- RAG AI --------------------
    response = rag_chain.invoke({"input": msg})
    ai_answer = str(response["answer"])
    print("AI Response:", ai_answer)

    # -------------------- Doctor Recommendation --------------------
    doctor_suggestion = get_ai_doctor_recommendation(msg)

    final_answer = (
        ai_answer
        + doctor_suggestion
        + "\n You can channel this specialist via eChannelling or Doc990."
    )

    print("Response:", final_answer)

    ai_message = {
        "session_id": current_session_id,
        "user_id": session['user_id'],
        "content": final_answer,
        "sender": "ai",
        "timestamp": get_local_time()
    }
    messages_collection.insert_one(ai_message)

    chat_sessions_collection.update_one(
        {"_id": ObjectId(current_session_id)},
        {
            "$set": {"last_activity": get_local_time()},
            "$inc": {"message_count": 2}
        }
    )

    session_obj = chat_sessions_collection.find_one({"_id": ObjectId(current_session_id)})
    if session_obj and session_obj.get('message_count', 0) <= 2:
        title = msg[:30] + "..." if len(msg) > 30 else msg
        if not title.strip():
            title = "New Chat"

        chat_sessions_collection.update_one(
            {"_id": ObjectId(current_session_id)},
            {"$set": {"title": title}}
        )

    return jsonify({"response": final_answer})

# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
