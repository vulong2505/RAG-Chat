# Local RAG Chat <img src="frontend/public/rag_favicon.svg" width="50" alt="Local RAG Chat Icon">

A chat application with an advanced, agentic RAG system. The RAG architecture implements the [Adaptive-RAG framework](https://arxiv.org/abs/2403.14403) with multi-query translation, intelligent workflow routing, self-reflection capabilities, and web search—all while keeping your data **local** and **private**.

## Table of Contents

- [Overview](#overview)
- [Advance RAG Workflow](#advance-rag-workflow)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
    - [Prerequisites](#prerequisites)
    - [Backend Setup](#backend-setup)
    - [Frontend Setup](#frontend-setup)
- [Reset the Database](#reset-the-database)

## Overview

https://github.com/user-attachments/assets/c4b0cc2e-da9f-40e9-96b2-11461f983b48
<div align="center">
  <p><em>Video 1: Demonstration of the local RAG chat and how queries are routed in the adaptive workflow. The first query utilizes the advanced RAG pipeline. The second query utilizes web search. And, the final query is generated directly without retrieval.</em></p>
</div>
## Advance RAG Workflow

Unlike a basic RAG implementation, this system features:

* **Adaptive Retrieval-Augmented Generation:** Dynamically chooses between vectorstore, web search, or direct generation based on query type
* **Multi-Query Translation:** Creates multiple semantic variations of your question for better retrieval.
* **Agentic Self-Reflection:** Agents grades the system's retrievals and generations, discarding irrelevant documents and regenerating hallucinated responses
* **Self-Correction:** The system will reformulate the original query to a better one when retrieval knowledge is insufficient.
* **Online Search:** Surf the Internet for sources on current news.


<div align="center">
  <img src="readme_data\rag_workflow.png" alt="RAG Workflow">
  <p><em>Figure 1: The advanced RAG workflow schematic. The adaptive RAG system can route the question to be answered directly, answered with web search, or answered with retrieval. This system also implements agentic self-reflection for better generation. </em></p>
</div>

This system implements a full LangGraph workflow with decision nodes, conditional routing, and self-correction capabilities that significantly improve over standard RAG patterns.

## Features

* **Local LLM**: Uses Ollama to run models like DeepSeek-R1 and Mistral locally on your machine.
* **Document Quality Assessment:** Automatically evaluates and filters retrieved documents for relevance
* **Question Reformulation:** Rewrites questions that don't yield good results to improve retrieval
* **Hallucination Detection:** Verifies generated responses against source documents
* **Web Search Integration:** Falls back to Tavily API for real-time information
* **Sources:** Answers with retrieval will cite the retrieved documentation chunks for better transparency.
* **Document Upload:** Supports PDF, TXT, and DOCX files with automatic chunking and embedding
* **Persistent Conversation History:** Complete chat history with SQLite backend

## Tech Stack

* **Backend:** FastAPI, LangChain, LangGraph, ChromaDB, SQLite
* **Frontend:** React + TypeScript, Tailwind CSS
* **LLM Serving:** Ollama (DeepSeek-R1 for chat, Mistral for RAG)
* **Vector Database:** ChromaDB with local persistence
* **Embedding Model:** Nomic AI's text embeddings running locally
* **Web Search:** Tavily API integration

## Setup Instructions

### Prerequisites
* Python 3.9+
* Node.js 16+
* Ollama installed
* Tavily API key

### Backend Setup

1. Clone the repository
```bash
git clone https://github.com/vulong2505/RAG-Chat.git
cd rag-chat
```

2. Create and activate a virtual environment
```bash
cd backend
py -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
py -m app.database.init_db
```

5. Add your Tavily API key to .env:
```bash
# backend/.env
echo "TAVILY_API_KEY=your-api-key-here" > .env
```

6. Start Ollama service and pull the required models:
```bash
ollama serve & # runs Ollama as a background process
ollama pull deepseek-r1:7b
ollama pull mistral
```

7. Start the backend server:
```bash
# Run backend/run.py
py run.py
```

### Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
```bash
# From RAG_Chat/
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Start the development server.
```bash
npm run dev
```

4. Open your browser and visit `http://localhost:5173`

## Reset the Database

To reset the ChromaDB vectorstore and SQLite database:
```bash
# from RAG_Chat/backend/
py -m app.database.reset_db
```
