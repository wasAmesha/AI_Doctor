# AI Medical Assistant ChatBot 🏥🤖

An intelligent medical chatbot designed to provide users with immediate and reliable medical support through natural language conversations. This system leverages advanced AI techniques to analyze symptoms, provide preliminary medical guidance, and recommend appropriate healthcare specialists.

## 🌟 Features

- **Symptom Analysis**: Intelligent analysis of user-described symptoms using natural language processing
- **Preliminary Medical Guidance**: Evidence-based suggestions for potential causes and treatment options
- **Doctor Recommendations**: Rule-based specialist mapping to guide users to appropriate healthcare professionals
- **Secure User Management**: Login system with personalized chat history and data privacy
- **Retrieval-Augmented Generation (RAG)**: Context-aware responses based on medical literature
- **Conversational Interface**: User-friendly chat interface supporting everyday language

## 🚨 Important Disclaimer

**This chatbot is NOT a replacement for professional medical advice, diagnosis, or treatment. It serves as a decision-support tool for preliminary guidance only. Always consult with qualified healthcare professionals for medical concerns.**

## 🏗️ Architecture

### Core Components

- **Text Processing Engine**: Preprocessing pipeline with lowercasing, stopword removal, lemmatization, and chunking
- **Vector Database**: Pinecone-based semantic search for medical knowledge retrieval
- **AI Agents**:
  - RAG-based QA Agent for medical question answering
  - Doctor Recommendation Agent for specialist suggestions
- **Large Language Models**: OpenAI API integration with fine-tuned medical models
- **Database**: MongoDB for secure user data and session management

### Technology Stack

- **Frontend**: Interactive chat interface
- **Backend**: Python-based AI agents and API services
- **Vector Database**: Pinecone for semantic search
- **Database**: MongoDB for user data storage
- **ML Models**:
  - `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract` for embeddings
  - OpenAI GPT models for response generation
- **Deployment**: Docker containers with CI/CD pipelines

## 📋 Prerequisites

- Python 3.8+
- Docker and Docker Compose
- MongoDB instance
- Pinecone API key
- OpenAI API key

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/wasAmesha/AI_Doctor
```

### 2. Environment Setup

Create a `.env` file in the root directory:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
HF_TOKEN=your_huggingface_token

# Database Configuration
MONGO_URI=mongodb://localhost:27017/medical_chatbot
DB_NAME=medical_chatbot

# Security
SECRET_KEY=your_secret_key
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 4. Run application

```bash
python app.py
```

## 📊 Usage

### Starting a Conversation

1. Register/Login to the system
2. Navigate to the chat interface
3. Describe your symptoms in natural language
4. Review the AI-generated response and recommendations
5. Follow up with additional questions as needed

### Example Interactions

```
User: "I have been experiencing chest pain and shortness of breath"
Bot: "Based on your symptoms, there are several possible causes ranging from cardiac issues to respiratory conditions. I recommend consulting with a cardiologist for proper evaluation. Here are some preliminary considerations..."

User: "What tests should I ask for?"
Bot: "Based on your chest pain and breathing symptoms, common diagnostic tests may include: ECG, chest X-ray, and blood tests. However, your doctor will determine the most appropriate tests based on your specific condition."
```

## 🔒 Security & Privacy

- **Data Encryption**: All sensitive data is encrypted at rest and in transit
- **User Authentication**: JWT-based authentication system
- **Privacy Compliance**: Designed with HIPAA/GDPR considerations
- **Session Management**: Secure session handling with automatic expiration
- **API Security**: Rate limiting and input validation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 References

- Gu, Y., et al. (2020). Domain-specific language model pretraining for biomedical natural language processing
- Microsoft BiomedNLP-PubMedBERT: [Hugging Face Model](https://huggingface.co/microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract)
- OpenAI API Documentation: [https://openai.com/api/](https://openai.com/api/)
- Pinecone Vector Database: [https://www.pinecone.io/](https://www.pinecone.io/)

## ⚖️ Medical Disclaimer

This software is for educational and informational purposes only. It is not intended as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. Never disregard professional medical advice or delay in seeking it because of something you have read or received from this chatbot.

---

**Built with ❤️ for better healthcare accessibility**
